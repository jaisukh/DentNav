"use client";

/* CREDIT: Component inspired by Can Tastemel's work (lambda.ai landing) — https://cantastemel.com */

import React, { useCallback, useEffect, useRef } from "react";
import type { CSSProperties } from "react";
import gsap from "gsap";

import "./Cubes.css";

interface Gap {
  row: number;
  col: number;
}
interface Duration {
  enter: number;
  leave: number;
}

export interface CubesProps {
  /** @deprecated Prefer gridCols + gridRows. If set, uses N×N grid. */
  gridSize?: number;
  /** Columns in the grid (width). */
  gridCols?: number;
  /** Rows in the grid (height). */
  gridRows?: number;
  cubeSize?: number;
  maxAngle?: number;
  /** Tilt/ripple neighborhood radius in grid cells */
  radius?: number;
  easing?: gsap.EaseString;
  duration?: Duration;
  cellGap?: number | Gap;
  borderStyle?: string;
  faceColor?: string;
  /** Corner radius on each face, e.g. 6 or "8px" */
  faceRadius?: number | string;
  shadow?: boolean | string;
  autoAnimate?: boolean;
  rippleOnClick?: boolean;
  rippleColor?: string;
  rippleSpeed?: number;
  className?: string;
}

const Cubes: React.FC<CubesProps> = ({
  gridSize,
  gridCols: gridColsProp,
  gridRows: gridRowsProp,
  cubeSize,
  maxAngle = 45,
  radius = 3,
  easing = "power3.out",
  duration = { enter: 0.3, leave: 0.6 },
  cellGap,
  borderStyle = "1px solid #fff",
  faceColor = "#060010",
  faceRadius = 6,
  shadow = false,
  autoAnimate = true,
  rippleOnClick = true,
  rippleColor = "#fff",
  rippleSpeed = 2,
  className = "",
}) => {
  const gridCols = gridColsProp ?? gridSize ?? 10;
  const gridRows = gridRowsProp ?? gridSize ?? 10;
  const sceneRef = useRef<HTMLDivElement | null>(null);
  const rafRef = useRef<number | null>(null);
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const userActiveRef = useRef(false);
  const simPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const simTargetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const simRAFRef = useRef<number | null>(null);

  const colGap =
    typeof cellGap === "number"
      ? `${cellGap}px`
      : (cellGap as Gap)?.col !== undefined
        ? `${(cellGap as Gap).col}px`
        : "5%";
  const rowGap =
    typeof cellGap === "number"
      ? `${cellGap}px`
      : (cellGap as Gap)?.row !== undefined
        ? `${(cellGap as Gap).row}px`
        : "5%";

  const enterDur = duration.enter;
  const leaveDur = duration.leave;

  const tiltAt = useCallback(
    (rowCenter: number, colCenter: number) => {
      if (!sceneRef.current) return;
      sceneRef.current.querySelectorAll<HTMLDivElement>(".cube").forEach((cube) => {
        const r = +cube.dataset.row!;
        const c = +cube.dataset.col!;
        const dist = Math.hypot(r - rowCenter, c - colCenter);
        if (dist <= radius) {
          const pct = 1 - dist / radius;
          const angle = pct * maxAngle;
          gsap.to(cube, {
            duration: enterDur,
            ease: easing,
            overwrite: true,
            rotateX: -angle,
            rotateY: angle,
          });
        } else {
          gsap.to(cube, {
            duration: leaveDur,
            ease: "power3.out",
            overwrite: true,
            rotateX: 0,
            rotateY: 0,
          });
        }
      });
    },
    [radius, maxAngle, enterDur, leaveDur, easing],
  );

  const onPointerMove = useCallback(
    (e: PointerEvent) => {
      userActiveRef.current = true;
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);

      const rect = sceneRef.current!.getBoundingClientRect();
      const cellW = rect.width / gridCols;
      const cellH = rect.height / gridRows;
      const colCenter = (e.clientX - rect.left) / cellW;
      const rowCenter = (e.clientY - rect.top) / cellH;

      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(() => tiltAt(rowCenter, colCenter));

      idleTimerRef.current = setTimeout(() => {
        userActiveRef.current = false;
      }, 3000);
    },
    [gridCols, gridRows, tiltAt],
  );

  const resetAll = useCallback(() => {
    if (!sceneRef.current) return;
    sceneRef.current.querySelectorAll<HTMLDivElement>(".cube").forEach((cube) =>
      gsap.to(cube, {
        duration: leaveDur,
        rotateX: 0,
        rotateY: 0,
        ease: "power3.out",
      }),
    );
  }, [leaveDur]);

  const onTouchMove = useCallback(
    (e: TouchEvent) => {
      e.preventDefault();
      userActiveRef.current = true;
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);

      const rect = sceneRef.current!.getBoundingClientRect();
      const cellW = rect.width / gridCols;
      const cellH = rect.height / gridRows;

      const touch = e.touches[0];
      const colCenter = (touch.clientX - rect.left) / cellW;
      const rowCenter = (touch.clientY - rect.top) / cellH;

      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      rafRef.current = requestAnimationFrame(() => tiltAt(rowCenter, colCenter));

      idleTimerRef.current = setTimeout(() => {
        userActiveRef.current = false;
      }, 3000);
    },
    [gridCols, gridRows, tiltAt],
  );

  const onTouchStart = useCallback(() => {
    userActiveRef.current = true;
  }, []);

  const onTouchEnd = useCallback(() => {
    if (!sceneRef.current) return;
    resetAll();
  }, [resetAll]);

  const onClick = useCallback(
    (e: MouseEvent | TouchEvent) => {
      if (!rippleOnClick || !sceneRef.current) return;
      const rect = sceneRef.current.getBoundingClientRect();
      const cellW = rect.width / gridCols;
      const cellH = rect.height / gridRows;

      const clientX =
        "clientX" in e && e.clientX != null
          ? e.clientX
          : (e as TouchEvent).touches?.[0]?.clientX ?? 0;
      const clientY =
        "clientY" in e && e.clientY != null
          ? e.clientY
          : (e as TouchEvent).touches?.[0]?.clientY ?? 0;

      const colHit = Math.floor((clientX - rect.left) / cellW);
      const rowHit = Math.floor((clientY - rect.top) / cellH);

      const baseRingDelay = 0.15;
      const baseAnimDur = 0.3;
      const baseHold = 0.6;

      const spreadDelay = baseRingDelay / rippleSpeed;
      const animDuration = baseAnimDur / rippleSpeed;
      const holdTime = baseHold / rippleSpeed;

      const rings: Record<number, HTMLDivElement[]> = {};
      sceneRef.current.querySelectorAll<HTMLDivElement>(".cube").forEach((cube) => {
        const r = +cube.dataset.row!;
        const c = +cube.dataset.col!;
        const dist = Math.hypot(r - rowHit, c - colHit);
        const ring = Math.round(dist);
        if (!rings[ring]) rings[ring] = [];
        rings[ring].push(cube);
      });

      Object.keys(rings)
        .map(Number)
        .sort((a, b) => a - b)
        .forEach((ring) => {
          const delay = ring * spreadDelay;
          const faces = rings[ring].flatMap((cube) =>
            Array.from(cube.querySelectorAll<HTMLElement>(".cube-face")),
          );

          gsap.to(faces, {
            backgroundColor: rippleColor,
            duration: animDuration,
            delay,
            ease: "power3.out",
          });
          gsap.to(faces, {
            backgroundColor: faceColor,
            duration: animDuration,
            delay: delay + animDuration + holdTime,
            ease: "power3.out",
          });
        });
    },
    [rippleOnClick, gridCols, gridRows, faceColor, rippleColor, rippleSpeed],
  );

  useEffect(() => {
    if (!autoAnimate || !sceneRef.current) return;
    simPosRef.current = {
      x: Math.random() * gridCols,
      y: Math.random() * gridRows,
    };
    simTargetRef.current = {
      x: Math.random() * gridCols,
      y: Math.random() * gridRows,
    };
    const speed = 0.02;
    const loop = () => {
      if (!userActiveRef.current) {
        const pos = simPosRef.current;
        const tgt = simTargetRef.current;
        pos.x += (tgt.x - pos.x) * speed;
        pos.y += (tgt.y - pos.y) * speed;
        tiltAt(pos.y, pos.x);
        if (Math.hypot(pos.x - tgt.x, pos.y - tgt.y) < 0.1) {
          simTargetRef.current = {
            x: Math.random() * gridCols,
            y: Math.random() * gridRows,
          };
        }
      }
      simRAFRef.current = requestAnimationFrame(loop);
    };
    simRAFRef.current = requestAnimationFrame(loop);
    return () => {
      if (simRAFRef.current != null) {
        cancelAnimationFrame(simRAFRef.current);
      }
    };
  }, [autoAnimate, gridCols, gridRows, tiltAt]);

  useEffect(() => {
    const el = sceneRef.current;
    if (!el) return;
    el.addEventListener("pointermove", onPointerMove);
    el.addEventListener("pointerleave", resetAll);
    el.addEventListener("click", onClick);

    el.addEventListener("touchmove", onTouchMove, { passive: false });
    el.addEventListener("touchstart", onTouchStart, { passive: true });
    el.addEventListener("touchend", onTouchEnd, { passive: true });

    return () => {
      el.removeEventListener("pointermove", onPointerMove);
      el.removeEventListener("pointerleave", resetAll);
      el.removeEventListener("click", onClick);

      el.removeEventListener("touchmove", onTouchMove);
      el.removeEventListener("touchstart", onTouchStart);
      el.removeEventListener("touchend", onTouchEnd);

      if (rafRef.current != null) {
        cancelAnimationFrame(rafRef.current);
      }
      if (idleTimerRef.current) {
        clearTimeout(idleTimerRef.current);
      }
    };
  }, [onPointerMove, resetAll, onClick, onTouchMove, onTouchStart, onTouchEnd]);

  const rowIndices = Array.from({ length: gridRows });
  const colIndices = Array.from({ length: gridCols });
  const sceneStyle: CSSProperties = {
    gridTemplateColumns: cubeSize
      ? `repeat(${gridCols}, ${cubeSize}px)`
      : `repeat(${gridCols}, 1fr)`,
    gridTemplateRows: cubeSize
      ? `repeat(${gridRows}, ${cubeSize}px)`
      : `repeat(${gridRows}, 1fr)`,
    columnGap: colGap,
    rowGap: rowGap,
  };
  const faceRadiusCss =
    typeof faceRadius === "number" ? `${faceRadius}px` : faceRadius;
  const wrapperStyle = {
    "--cube-face-border": borderStyle,
    "--cube-face-bg": faceColor,
    "--cube-face-radius": faceRadiusCss,
    "--cubes-aspect": `${gridCols} / ${gridRows}`,
    "--cube-face-shadow":
      shadow === true ? "0 0 6px rgba(0,0,0,.5)" : shadow || "none",
    ...(cubeSize
      ? {
          width: `${gridCols * cubeSize}px`,
          height: `${gridRows * cubeSize}px`,
        }
      : {}),
  } as CSSProperties;

  return (
    <div className={`default-animation ${className}`.trim()} style={wrapperStyle}>
      <div ref={sceneRef} className="default-animation--scene" style={sceneStyle}>
        {rowIndices.map((_, r) =>
          colIndices.map((__, c) => (
            <div key={`${r}-${c}`} className="cube" data-row={r} data-col={c}>
              <div className="cube-face cube-face--top" />
              <div className="cube-face cube-face--bottom" />
              <div className="cube-face cube-face--left" />
              <div className="cube-face cube-face--right" />
              <div className="cube-face cube-face--front" />
              <div className="cube-face cube-face--back" />
            </div>
          )),
        )}
      </div>
    </div>
  );
};

export default Cubes;
