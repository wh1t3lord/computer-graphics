
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


[shader("vertex")]
OUT_VERTEX mainVertex(IN_VERTEX in_args)
{
    OUT_VERTEX result;
    result.color = float3(1.0f, 0.0f, 0.0f);
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