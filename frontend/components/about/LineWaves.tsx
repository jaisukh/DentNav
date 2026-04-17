"use client";

import { useEffect, useRef } from "react";
import { Mesh, Program, Renderer, Triangle } from "ogl";

export type LineWavesProps = {
  speed?: number;
  innerLineCount?: number;
  outerLineCount?: number;
  warpIntensity?: number;
  rotation?: number;
  edgeFadeWidth?: number;
  colorCycleSpeed?: number;
  brightness?: number;
  color1?: string;
  color2?: string;
  color3?: string;
  enableMouseInteraction?: boolean;
  mouseInfluence?: number;
  className?: string;
};

function hexToVec3(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  if (h.length !== 6) {
    return [1, 1, 1];
  }
  return [
    parseInt(h.slice(0, 2), 16) / 255,
    parseInt(h.slice(2, 4), 16) / 255,
    parseInt(h.slice(4, 6), 16) / 255,
  ];
}

const vertexShader = /* glsl */ `
attribute vec2 uv;
attribute vec2 position;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}
`;

const fragmentShader = /* glsl */ `
precision highp float;

uniform float uTime;
uniform vec3 uResolution;
uniform float uSpeed;
uniform float uInnerLines;
uniform float uOuterLines;
uniform float uWarpIntensity;
uniform float uRotation;
uniform float uEdgeFadeWidth;
uniform float uColorCycleSpeed;
uniform float uBrightness;
uniform vec3 uColor1;
uniform vec3 uColor2;
uniform vec3 uColor3;
uniform vec2 uMouse;
uniform float uMouseInfluence;
uniform float uEnableMouse;

#define HALF_PI 1.5707963

float hashF(float n) {
  return fract(sin(n * 127.1) * 43758.5453123);
}

float smoothNoise(float x) {
  float i = floor(x);
  float f = fract(x);
  float u = f * f * (3.0 - 2.0 * f);
  return mix(hashF(i), hashF(i + 1.0), u);
}

float displaceA(float coord, float t) {
  float result = sin(coord * 2.123) * 0.2;
  result += sin(coord * 3.234 + t * 4.345) * 0.1;
  result += sin(coord * 0.589 + t * 0.934) * 0.5;
  return result;
}

float displaceB(float coord, float t) {
  float result = sin(coord * 1.345) * 0.3;
  result += sin(coord * 2.734 + t * 3.345) * 0.2;
  result += sin(coord * 0.189 + t * 0.934) * 0.3;
  return result;
}

vec2 rotate2D(vec2 p, float angle) {
  float c = cos(angle);
  float s = sin(angle);
  return vec2(p.x * c - p.y * s, p.x * s + p.y * c);
}

void main() {
  vec2 coords = gl_FragCoord.xy / uResolution.xy;
  coords = coords * 2.0 - 1.0;
  coords = rotate2D(coords, uRotation);

  float halfT = uTime * uSpeed * 0.5;
  float fullT = uTime * uSpeed;

  float mouseWarp = 0.0;
  if (uEnableMouse > 0.5) {
    vec2 mPos = rotate2D(uMouse * 2.0 - 1.0, uRotation);
    float mDist = length(coords - mPos);
    // Wider falloff than exp(-4*mDist^2) so the effect reads across the hero (was ~invisible).
    float falloff = exp(-mDist * mDist * 0.55);
    mouseWarp = uMouseInfluence * 0.35 * falloff;
  }

  float warpAx = coords.x + displaceA(coords.y, halfT) * uWarpIntensity + mouseWarp;
  float warpAy = coords.y - displaceA(coords.x * cos(fullT) * 1.235, halfT) * uWarpIntensity + mouseWarp * 0.65;
  float warpBx = coords.x + displaceB(coords.y, halfT) * uWarpIntensity + mouseWarp;
  float warpBy = coords.y - displaceB(coords.x * sin(fullT) * 1.235, halfT) * uWarpIntensity + mouseWarp * 0.65;

  vec2 fieldA = vec2(warpAx, warpAy);
  vec2 fieldB = vec2(warpBx, warpBy);
  vec2 blended = mix(fieldA, fieldB, mix(fieldA, fieldB, 0.5));

  float fadeTop = smoothstep(uEdgeFadeWidth, uEdgeFadeWidth + 0.4, blended.y);
  float fadeBottom = smoothstep(-uEdgeFadeWidth, -(uEdgeFadeWidth + 0.4), blended.y);
  float vMask = 1.0 - max(fadeTop, fadeBottom);

  float tileCount = mix(uOuterLines, uInnerLines, vMask);
  float scaledY = blended.y * tileCount;
  float nY = smoothNoise(abs(scaledY));

  float ridge = pow(
    step(abs(nY - blended.x) * 2.0, HALF_PI) * cos(2.0 * (nY - blended.x)),
    5.0
  );

  float lines = 0.0;
  for (float i = 1.0; i < 3.0; i += 1.0) {
    lines += pow(max(fract(scaledY), fract(-scaledY)), i * 2.0);
  }

  float pattern = vMask * lines;

  float cycleT = fullT * uColorCycleSpeed;
  float rChannel = (pattern + lines * ridge) * (cos(blended.y + cycleT * 0.234) * 0.5 + 1.0);
  float gChannel = (pattern + vMask * ridge) * (sin(blended.x + cycleT * 1.745) * 0.5 + 1.0);
  float bChannel = (pattern + lines * ridge) * (cos(blended.x + cycleT * 0.534) * 0.5 + 1.0);

  vec3 col = (rChannel * uColor1 + gChannel * uColor2 + bChannel * uColor3) * uBrightness;
  float alpha = clamp(length(col), 0.0, 1.0);

  gl_FragColor = vec4(col, alpha);
}
`;

export default function LineWaves({
  speed = 0.05,
  innerLineCount = 32,
  outerLineCount = 36,
  warpIntensity = 0.5,
  rotation = 45,
  edgeFadeWidth = 0,
  colorCycleSpeed = 1,
  brightness = 0.2,
  color1 = "#ffffff",
  color2 = "#ffffff",
  color3 = "#ffffff",
  enableMouseInteraction = true,
  mouseInfluence = 2,
  className = "",
}: LineWavesProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const propsRef = useRef({
    speed,
    innerLineCount,
    outerLineCount,
    warpIntensity,
    rotation,
    edgeFadeWidth,
    colorCycleSpeed,
    brightness,
    color1,
    color2,
    color3,
    enableMouseInteraction,
    mouseInfluence,
  });
  propsRef.current = {
    speed,
    innerLineCount,
    outerLineCount,
    warpIntensity,
    rotation,
    edgeFadeWidth,
    colorCycleSpeed,
    brightness,
    color1,
    color2,
    color3,
    enableMouseInteraction,
    mouseInfluence,
  };

  useEffect(() => {
    const root = containerRef.current;
    if (!root) return;

    const renderer = new Renderer({
      alpha: true,
      premultipliedAlpha: false,
      antialias: true,
    });
    const gl = renderer.gl;
    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    const canvas = gl.canvas as HTMLCanvasElement;
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.display = "block";

    let program!: Program;
    const currentMouse = [0.5, 0.5];
    const targetMouse = [0.5, 0.5];

    function boundsElement(): HTMLElement | null {
      const inner = containerRef.current;
      if (!inner) return null;
      return (
        (inner.closest("[data-line-waves-bounds]") as HTMLElement | null) ??
        inner
      );
    }

    /** Hero-sized container is under content; use window pointer + bounds so warping works over text too. */
    function handlePointerMove(e: PointerEvent | MouseEvent) {
      const el = boundsElement();
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const inside =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top &&
        e.clientY <= rect.bottom;
      if (inside) {
        const nx = (e.clientX - rect.left) / Math.max(1, rect.width);
        const ny = 1 - (e.clientY - rect.top) / Math.max(1, rect.height);
        targetMouse[0] = Math.min(1, Math.max(0, nx));
        targetMouse[1] = Math.min(1, Math.max(0, ny));
      } else {
        targetMouse[0] = 0.5;
        targetMouse[1] = 0.5;
      }
    }

    function handlePointerLeaveWindow() {
      targetMouse[0] = 0.5;
      targetMouse[1] = 0.5;
    }

    function resize() {
      const el = containerRef.current;
      if (!el) return;
      const w = Math.max(1, el.offsetWidth);
      const h = Math.max(1, el.offsetHeight);
      renderer.setSize(w, h);
      program.uniforms.uResolution.value = [
        gl.canvas.width,
        gl.canvas.height,
        gl.canvas.width / gl.canvas.height,
      ];
    }

    window.addEventListener("resize", resize);

    const geometry = new Triangle(gl);
    const p = propsRef.current;
    const rotationRad = (p.rotation * Math.PI) / 180;

    program = new Program(gl, {
      vertex: vertexShader,
      fragment: fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uResolution: {
          value: [1, 1, 1],
        },
        uSpeed: { value: p.speed },
        uInnerLines: { value: p.innerLineCount },
        uOuterLines: { value: p.outerLineCount },
        uWarpIntensity: { value: p.warpIntensity },
        uRotation: { value: rotationRad },
        uEdgeFadeWidth: { value: p.edgeFadeWidth },
        uColorCycleSpeed: { value: p.colorCycleSpeed },
        uBrightness: { value: p.brightness },
        uColor1: { value: hexToVec3(p.color1) },
        uColor2: { value: hexToVec3(p.color2) },
        uColor3: { value: hexToVec3(p.color3) },
        uMouse: { value: new Float32Array([0.5, 0.5]) },
        uMouseInfluence: { value: p.mouseInfluence },
        uEnableMouse: { value: p.enableMouseInteraction ? 1 : 0 },
      },
    });

    const mesh = new Mesh(gl, { geometry, program });
    root.appendChild(canvas);

    if (p.enableMouseInteraction) {
      window.addEventListener("pointermove", handlePointerMove, { passive: true });
      window.addEventListener("mousemove", handlePointerMove, { passive: true });
      window.addEventListener("blur", handlePointerLeaveWindow);
    }

    resize();

    let animationFrameId = 0;

    function update(time: number) {
      animationFrameId = requestAnimationFrame(update);
      const pr = propsRef.current;
      program.uniforms.uTime.value = time * 0.001;
      program.uniforms.uSpeed.value = pr.speed;
      program.uniforms.uInnerLines.value = pr.innerLineCount;
      program.uniforms.uOuterLines.value = pr.outerLineCount;
      program.uniforms.uWarpIntensity.value = pr.warpIntensity;
      program.uniforms.uRotation.value = (pr.rotation * Math.PI) / 180;
      program.uniforms.uEdgeFadeWidth.value = pr.edgeFadeWidth;
      program.uniforms.uColorCycleSpeed.value = pr.colorCycleSpeed;
      program.uniforms.uBrightness.value = pr.brightness;
      program.uniforms.uColor1.value = hexToVec3(pr.color1);
      program.uniforms.uColor2.value = hexToVec3(pr.color2);
      program.uniforms.uColor3.value = hexToVec3(pr.color3);
      program.uniforms.uMouseInfluence.value = pr.mouseInfluence;
      program.uniforms.uEnableMouse.value = pr.enableMouseInteraction ? 1 : 0;

      if (pr.enableMouseInteraction) {
        const follow = 0.22;
        currentMouse[0] += follow * (targetMouse[0] - currentMouse[0]);
        currentMouse[1] += follow * (targetMouse[1] - currentMouse[1]);
        // New Float32Array each frame so ogl's uniform cache always uploads (in-place mutation can skip).
        program.uniforms.uMouse.value = new Float32Array([
          currentMouse[0],
          currentMouse[1],
        ]);
      } else {
        program.uniforms.uMouse.value = new Float32Array([0.5, 0.5]);
      }

      renderer.render({ scene: mesh });
    }
    animationFrameId = requestAnimationFrame(update);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resize);
      if (p.enableMouseInteraction) {
        window.removeEventListener("pointermove", handlePointerMove);
        window.removeEventListener("mousemove", handlePointerMove);
        window.removeEventListener("blur", handlePointerLeaveWindow);
      }
      if (root.contains(canvas)) {
        root.removeChild(canvas);
      }
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={`h-full min-h-[240px] w-full ${className}`}
      aria-hidden
    />
  );
}
