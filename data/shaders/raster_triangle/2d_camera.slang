
struct IN_VERTEX
{
    float3 pos : POSITION;
}

struct OUT_VERTEX
{
    float3 color;
    float4 pos : SV_POSITION;
}

struct OUT_PIXEL
{
    float4 color : COLOR;
}

uniform float3 g_TriangleColor;
uniform float4x4 g_mModel;
uniform float4x4 g_mView;
uniform float4x4 g_mProjection;

[shader("vertex")]
OUT_VERTEX mainVertex(IN_VERTEX in_args)
{
    OUT_VERTEX result;
    result.color = g_TriangleColor;
    result.pos = mul(float4(in_args.pos, 1.0), g_mModel);
    result.pos = mul(result.pos, g_mView);
    result.pos = mul(result.pos, g_mProjection);

    return result;
}

[shader("fragment")]
OUT_PIXEL mainPixel(OUT_VERTEX in_args)
{
    OUT_PIXEL result;
    result.color = float4(in_args.color.xyz, 1.0);

    return result;
}