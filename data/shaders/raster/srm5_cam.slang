
struct IN_VERTEX
{
    float3 pos : POSITION;
    float3 color : COLOR;
    float2 uv : TEXCOORD;
}

struct OUT_VERTEX
{
    float3 color;
    float2 uv;
    float4 pos : SV_POSITION;
}

struct OUT_PIXEL
{
    float4 color : COLOR;
}

struct LIGHT_AMBIENT_DATA
{
    float3 color;
    float intensity;
}

uniform float4x4 g_mModel;
uniform float4x4 g_mView;
uniform float4x4 g_mProjection;
uniform LIGHT_AMBIENT_DATA g_lightAmbient;

Texture2D<float4> g_texture;
SamplerState g_sampler;

[shader("vertex")]
OUT_VERTEX mainVertex(IN_VERTEX in_args)
{
    OUT_VERTEX result;
    result.color = in_args.color;
    result.uv = in_args.uv;

    result.pos = mul(g_mModel, float4(in_args.pos, 1.0));
    result.pos = mul(g_mView, result.pos);
    result.pos = mul(g_mProjection, result.pos);

    return result;
}

[shader("fragment")]
OUT_PIXEL mainPixel(OUT_VERTEX in_args)
{
    OUT_PIXEL result;
    float4 vTexColor = g_texture.Sample(g_sampler, in_args.uv);
    float3 vAmbient = g_lightAmbient.color * g_lightAmbient.intensity;
    vTexColor.rgb *= vAmbient;
    result.color = vTexColor;

    return result;
}