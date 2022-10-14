VERTEX_SHADER_SOURCE = """
attribute vec2 position;

uniform float scale;
uniform vec2 shift;
uniform vec2 screenSize;
uniform vec2 canvasSize;

varying vec2 uv;

void main()
{
    vec2 wShift = vec2(shift.x, -shift.y);
    vec2 pos = ((position * 0.5 + vec2(0.5, -0.5)) * canvasSize * scale + wShift) / screenSize;
    gl_Position = vec4(pos * 2, 0.0, 1.0);

    uv = (position * 0.5 + 0.5);
    uv.y = 1.0 - uv.y;
}
"""

FRAGMENT_SHADER_SOURCE = """
uniform sampler2D textureSampler;

varying vec2 uv;

vec3 lerp(vec3 a, vec3 b, float x) {
    return a + (b - a) * x;
}

void main()
{
    vec4 color = texture2D(textureSampler, uv);

    vec3 backgroundColor = vec3(0.2);

    if(int(gl_FragCoord.x / 10) % 2 + int(gl_FragCoord.y / 10) % 2 == 1) {
        backgroundColor = vec3(0.3);
    }

    gl_FragColor = vec4(lerp(backgroundColor, color.rgb, color.a), 1.0);
}
"""
