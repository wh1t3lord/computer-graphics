
struct IN_VERTEX
{
    float2 pos : POSITION;
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

[shader("vertex")]
OUT_VERTEX mainVertex(IN_VERTEX in_args)
{
    OUT_VERTEX result;
    result.color = g_TriangleColor;
    result.pos = float4(in_args.pos.x, in_args.pos.y, 0.0, 1.0);

    return result;
}

[shader("fragment")]
OUT_PIXEL mainPixel(OUT_VERTEX in_args)
{
    OUT_PIXEL result;
    result.color = float4(in_args.color.xyz, 1.0);

    return result;
}