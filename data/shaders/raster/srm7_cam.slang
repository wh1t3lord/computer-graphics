
struct IN_VERTEX
{
    float3 pos : POSITION;
    float3 color : COLOR;
    float3 normal : NORMAL;
    float2 uv : TEXCOORD;
}

struct OUT_VERTEX
{
    float3 color;
    float3 worldNormal;
    float3 worldPosition;
    float2 uv;
    float4 pos : SV_POSITION;
}

struct OUT_PIXEL 
{
    float4 color : COLOR;
}

struct LIGHT_AMBIENT_DATA
{
    float3 intensity_ambient;
    float3 intensity_diffuse;
    float3 intensity_specular;
    float3 worldPosition;
}

struct MATERIAL_BLINN_PHONG
{
    Texture2D<float4> texture_diffuse;
    Texture2D<float4> texture_specular;
    float3 color_specular;
    float specular_shininess;
};

uniform float4x4 g_mModel;
uniform float4x4 g_mView;
uniform float4x4 g_mProjection;
uniform LIGHT_AMBIENT_DATA g_lightAmbient;
uniform float3 g_vCameraWorldPosition;
uniform MATERIAL_BLINN_PHONG g_materialBlinnPhong;

SamplerState g_sampler;

float3x3 inverse_mat(float3x3 m)
{
    // --- PHASE 1: Compute all 2x2 minors (shared by both det and adjugate) ---
    // We compute the 9 elements of the adjugate transpose directly.
    // For matrix M = [c0 c1 c2] where ci are column vectors:
    //
    // adj(M)^T = [ (m11*m22 - m12*m21), -(m01*m22 - m02*m21),  (m01*m12 - m02*m11) ]
    //            [-(m10*m22 - m12*m20),  (m00*m22 - m02*m20), -(m00*m12 - m02*m10) ]
    //            [ (m10*m21 - m11*m20), -(m00*m21 - m01*m20),  (m00*m11 - m01*m10) ]
    //
    // Key insight: Each row of adj(M)^T shares the SAME pair of cross-products!
    // Row 0 uses pairs from columns 1&2, Row 1 from columns 0&2, Row 2 from columns 0&1

    // Extract scalar components with optimal swizzling
    // RDNA3: These are free vector ALU ops, no extra registers
    float m00 = m[0][0], m01 = m[1][0], m02 = m[2][0];
    float m10 = m[0][1], m11 = m[1][1], m12 = m[2][1];
    float m20 = m[0][2], m21 = m[1][2], m22 = m[2][2];

    // --- PHASE 2: Compute cross-products for each column pair ---
    // These are the 2x2 determinants reused across adjugate and det
    // We compute 6 unique products, then derive the rest via negation

    // Column pair (1,2) cross-products: used for det00, det01, det02
    float cp_12_0 = m11 * m22; // m11*m22
    float cp_12_1 = m12 * m21; // m12*m21

    // Column pair (0,2) cross-products: used for det10, det11, det12
    float cp_02_0 = m10 * m22; // m10*m22
    float cp_02_1 = m12 * m20; // m12*m20

    // Column pair (0,1) cross-products: used for det20, det21, det22
    float cp_01_0 = m10 * m21; // m10*m21
    float cp_01_1 = m11 * m20; // m11*m20

    // --- PHASE 3: Construct adjugate transpose with FMA-friendly ops ---
    // Each element = (positive cross-product) - (negative cross-product)
    // Compiler emits: v_mad_f32 or v_fma_f32 where possible

    float3 row0, row1, row2;

    // Row 0: cofactors of row 0 (minors from columns 1,2)
    row0[0] = cp_12_0 - cp_12_1;     // C00 = +(m11*m22 - m12*m21)
    row0[1] = m02 * m21 - m01 * m22; // C01 = -(m01*m22 - m02*m21) = m02*m21 - m01*m22
    row0[2] = m01 * m12 - m02 * m11; // C02 = +(m01*m12 - m02*m11)

    // Row 1: cofactors of row 1 (minors from columns 0,2)
    row1[0] = m12 * m20 - m10 * m22; // C10 = -(m10*m22 - m12*m20) = m12*m20 - cp_02_0
    row1[1] = m00 * m22 - m02 * m20; // C11 = +(m00*m22 - m02*m20)
    row1[2] = m02 * m10 - m00 * m12; // C12 = -(m00*m12 - m02*m10) = m02*m10 - m00*m12

    // Row 2: cofactors of row 2 (minors from columns 0,1)
    row2[0] = cp_01_0 - cp_01_1;     // C20 = +(m10*m21 - m11*m20)
    row2[1] = m01 * m20 - m00 * m21; // C21 = -(m00*m21 - m01*m20) = m01*m20 - m00*m21
    row2[2] = m00 * m11 - m01 * m10; // C22 = +(m00*m11 - m01*m10)

    // --- PHASE 4: Determinant via Laplace expansion (reuse first row of adjugate) ---
    // det = m00*C00 + m01*C01 + m02*C02
    // We already have C00, C01, C02 in row0. Use dot product for FMA chain.
    float det = m00 * row0[0] + m01 * row0[1] + m02 * row0[2];

    // --- PHASE 5: Scalar reciprocal for vector multiply ---
    // rcp is ~4x faster than div on RDNA3/Ada. Use precise for accuracy.
    // For non-singular matrices in graphics, precise rcp is sufficient.
    float invDet = 1.0f / det; // Compiles to v_rcp_f32 on GCN/RDNA, rcp.approx on NV

    // --- PHASE 6: Scale adjugate transpose by 1/det ---
    // Vector multiply is 1 instruction per row on modern GPUs
    // Result is (1/det) * adj(M)^T which equals M^-1
    float3x3 inv;
    inv[0] = row0 * invDet;
    inv[1] = row1 * invDet;
    inv[2] = row2 * invDet;

    return inv;
}

[shader("vertex")]
OUT_VERTEX mainVertex(IN_VERTEX in_args)
{
    OUT_VERTEX result;
    result.color = in_args.color;
    result.uv = in_args.uv;

    result.pos = mul(g_mModel, float4(in_args.pos, 1.0));
    result.worldPosition = result.pos.xyz;
    result.pos = mul(g_mView, result.pos);
    result.pos = mul(g_mProjection, result.pos);

    float3x3 mNormal = transpose(inverse_mat(float3x3(g_mModel)));
    result.worldNormal = mul(mNormal, in_args.normal);

    return result;
}

[shader("fragment")]
OUT_PIXEL mainPixel(OUT_VERTEX in_args)
{
    OUT_PIXEL result;
    float4 vTexDiffuseColor = g_materialBlinnPhong.texture_diffuse.Sample(g_sampler, in_args.uv);

    float3 vAmbientColor = vTexDiffuseColor.rgb * g_lightAmbient.intensity_ambient;

    float3 vNorm = normalize(in_args.worldNormal);

    float3 vLightDir = normalize(g_lightAmbient.worldPosition - in_args.worldPosition.xyz);
    float fDiffuseIntensity = max(dot(vNorm, vLightDir), 0.0);
    float3 vDiffuseColor = fDiffuseIntensity * g_lightAmbient.intensity_diffuse * vTexDiffuseColor.rgb;

    float3 vViewDir = normalize(g_vCameraWorldPosition - in_args.worldPosition);
    // ofc we can use reflect as reflect(-vLightDir, vNorm), but we need to understand how the reflect works
    // we have a given normal (vNorm) and incident vector (vLightDir)
    // and the formula for
    // float3 vReflectDir = -vLightDir - (2.0 * (dot(vNorm, -vLightDir)) * vNorm);
    float3 vReflectDir = reflect(-vLightDir, vNorm);
    float fSpecularPower = pow(max(dot(vViewDir, vReflectDir), 0.0), g_materialBlinnPhong.specular_shininess);
    float3 vSpecularColor = fSpecularPower * g_lightAmbient.intensity_specular * g_materialBlinnPhong.texture_specular.Sample(g_sampler, in_args.uv).rgb;


    result.color.rgb = (vAmbientColor + vDiffuseColor + vSpecularColor);
    result.color.a = 1.0;

    return result;
}       