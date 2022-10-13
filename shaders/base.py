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

void main()
{
    gl_FragColor = texture2D(textureSampler, uv);
}
"""
