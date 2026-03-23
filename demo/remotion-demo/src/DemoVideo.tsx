import React from "react";
import {
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
  OffthreadVideo,
  AbsoluteFill,
} from "remotion";

// ── Timing (30fps, 105s total) ──
const FPS = 30;
const HOOK_DUR = 150;       // 5s
const PROBLEM_DUR = 120;    // 4s
const THESIS_DUR = 180;     // 6s
const PIPELINE_DUR = 840;   // 28s — the hero section
const OUTPUT_DUR = 450;     // 15s
const ONCHAIN_DUR = 540;    // 18s
const RARE_DUR = 420;       // 14s
const CLOSE_DUR = 450;      // 15s
const TOTAL = HOOK_DUR + PROBLEM_DUR + THESIS_DUR + PIPELINE_DUR + OUTPUT_DUR + ONCHAIN_DUR + RARE_DUR + CLOSE_DUR; // 3150 = 105s

// ── Colors ──
const C = {
  bg: "#050505",
  text: "#e4e4e7",
  dim: "#71717a",
  green: "#4ade80",
  purple: "#c084fc",
  blue: "#38bdf8",
  orange: "#f97316",
  yellow: "#facc15",
  red: "#f87171",
  terminal: "#0d1117",
  terminalBorder: "#21262d",
  cardBg: "#0d1117",
  accent: "#a78bfa",
};

// ── Easing helpers ──
const easeOut = Easing.out(Easing.cubic);
const easeIn = Easing.in(Easing.cubic);
const easeInOut = Easing.inOut(Easing.cubic);

// ── Film grain overlay ──
const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.04 }) => {
  const frame = useCurrentFrame();
  const seed = frame * 7919 % 10000;
  return (
    <AbsoluteFill
      style={{
        opacity,
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E")`,
        backgroundSize: "128px 128px",
        backgroundPosition: `${seed % 128}px ${seed * 3 % 128}px`,
        mixBlendMode: "overlay",
        pointerEvents: "none",
      }}
    />
  );
};

// ── Monospace text helper ──
const Mono = ({ children, color = C.text, size = 16, ...props }: { children: React.ReactNode; color?: string; size?: number; weight?: number; opacity?: number; [key: string]: unknown }) => (
  <span
    style={{
      fontFamily: "'JetBrains Mono', 'SF Mono', 'Fira Code', 'Courier New', monospace",
      fontSize: size,
      color,
      fontWeight: props.weight || 400,
      opacity: props.opacity,
      letterSpacing: "0.02em",
    }}
  >
    {children}
  </span>
);

// ── Animate-in wrapper ──
const FadeIn: React.FC<React.PropsWithChildren<{ delay: number; duration?: number; direction?: "up" | "down" | "left" | "none" }>> = ({
  delay,
  duration = 20,
  direction = "up",
  children,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const eased = easeOut(progress);
  const opacity = eased;
  const translateY = direction === "up" ? (1 - eased) * 20 : direction === "down" ? (1 - eased) * -20 : 0;
  const translateX = direction === "left" ? (1 - eased) * 30 : 0;

  return (
    <div style={{ opacity, transform: `translate(${translateX}px, ${translateY}px)` }}>
      {children}
    </div>
  );
};

// ── Scene 1: HOOK (0-5s) ──
const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();

  // Title reveals with a glitch-like snap
  const titleY = spring({ frame, fps: FPS, from: 40, to: 0, durationInFrames: 12, config: { damping: 20, stiffness: 200 } });
  const titleOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const titleScale = spring({ frame, fps: FPS, from: 0.95, to: 1, durationInFrames: 20, config: { damping: 15, stiffness: 150 } });

  const lineOpacity = interpolate(frame, [30, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lineY = interpolate(frame, [30, 60], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const scanline = interpolate(frame, [0, 150], [0, 1080], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      {/* Scanline pass */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 2,
          backgroundColor: `rgba(167, 139, 250, ${interpolate(frame, [60, 150], [0.6, 0], { extrapolateRight: "clamp" })})`,
          boxShadow: "0 0 20px 4px rgba(167, 139, 250, 0.3)",
          transform: `translateY(${scanline}px)`,
        }}
      />

      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px) scale(${titleScale})` }}>
          <Mono color="#fff" size={140} weight={700}>
            0xAUTEUR
          </Mono>
        </div>
        <div style={{ opacity: lineOpacity, transform: `translateY(${lineY}px)`, marginTop: 40 }}>
          <Mono color={C.accent} size={24}>
            Cinematic intelligence for autonomous agents
          </Mono>
        </div>
      </div>
      <Grain opacity={0.06} />
    </AbsoluteFill>
  );
};

// ── Scene 2: PROBLEM (5-9s) ──
const PROBLEMS = [
  { text: "blurry AI video with 6 fingers", icon: "✗" },
  { text: "flat lighting, no composition", icon: "✗" },
  { text: "inconsistent style across shots", icon: "✗" },
  { text: "no narrative structure", icon: "✗" },
];

const SceneProblem: React.FC = () => {
  const frame = useCurrentFrame();

  const items = PROBLEMS.map((_, i) => {
    const start = 10 + i * 22;
    const opacity = interpolate(frame, [start, start + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const x = interpolate(frame, [start, start + 10], [-40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return { ...PROBLEMS[i], opacity, x, eased: easeOut(opacity) };
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [100, 120], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, opacity: fadeIn * fadeOut }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 160px" }}>
        <FadeIn delay={0} duration={12}>
          <Mono color={C.red} size={48} weight={600}>
            AI video generation is broken
          </Mono>
        </FadeIn>
        <div style={{ marginTop: 50, display: "flex", flexDirection: "column", gap: 18 }}>
          {items.map((item, i) => (
            <div key={i} style={{ opacity: item.opacity, transform: `translateX(${item.x}px)`, display: "flex", alignItems: "center", gap: 16 }}>
              <Mono color={C.red} size={24}>{item.icon}</Mono>
              <Mono color={C.dim} size={22}>{item.text}</Mono>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: THESIS (9-15s) ──
const SceneThesis: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [155, 180], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Animated underline
  const lineWidth = interpolate(frame, [40, 70], [0, 380], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut });

  const featureOpacity = interpolate(frame, [70, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, opacity: fadeIn * fadeOut }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <FadeIn delay={5} duration={15}>
          <Mono color="#fff" size={56} weight={600}>
            The fix: encode filmmaking knowledge
          </Mono>
        </FadeIn>
        <div
          style={{
            width: lineWidth,
            height: 2,
            backgroundColor: C.accent,
            marginTop: 24,
            boxShadow: "0 0 12px rgba(167, 139, 250, 0.4)",
          }}
        />
        <div style={{ opacity: featureOpacity, marginTop: 50, display: "flex", gap: 60 }}>
          {[
            { label: "Aristotelian beats", sub: "dramatic structure" },
            { label: "Meisner acting", sub: "emotional truth" },
            { label: "DP profiles", sub: "Deakins · Lubezki · Storaro · Hoytema" },
            { label: "Onchain proof", sub: "Base · x402 · Rare Protocol" },
          ].map((f, i) => (
            <FadeIn key={i} delay={80 + i * 15} duration={15}>
              <div style={{ textAlign: "center" }}>
                <Mono color={C.accent} size={22} weight={500}>{f.label}</Mono>
                <div style={{ marginTop: 8 }}>
                  <Mono color={C.dim} size={14}>{f.sub}</Mono>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
        <FadeIn delay={130} duration={15}>
          <div style={{ marginTop: 60 }}>
            <Mono color={C.green} size={20}>All exposed as MCP tools. Composable. Pay-per-call.</Mono>
          </div>
        </FadeIn>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ── Scene 4: PIPELINE (15-43s) — Animated tool calling ──
type ToolCall = {
  tool: string;
  input: Record<string, string>;
  output: string;
  color: string;
  icon: string;
};

const TOOL_CALLS: ToolCall[] = [
  {
    tool: "analyse_brief",
    input: { logline: "Salt flat, blinding white, noon sun. A battered ute tears across the flat at speed. Pursued by bikies.", style: "Mad Max — Super 16" },
    output: "Project created: 8 beats, 25 shots, 4 characters",
    color: C.blue,
    icon: "01",
  },
  {
    tool: "propose_visual_language",
    input: { style_description: "bleached white salt / phosphor green terminal / bikie silhouettes", auteur_weight: "0.7" },
    output: "AuteurLayer: Hoytema 44% | Lubezki 14% | Storaro 12%",
    color: C.yellow,
    icon: "02",
  },
  {
    tool: "plan_shots",
    input: { pacing: "tension_build", shots_count: "25", tension_range: "0.2 → 0.95" },
    output: "25 shots mapped across 8 beats. Climax at beat 7.",
    color: C.orange,
    icon: "03",
  },
  {
    tool: "compose_prompt",
    input: { shot: "24_climax", camera: "ARRI Alexa Mini LF 35mm T1.4", movement: "handheld pursuit" },
    output: "Wide tracking shot, handheld Super 16mm... (847 chars)",
    color: C.purple,
    icon: "04",
  },
  {
    tool: "sanitise_and_submit",
    input: { model: "kling-3.0", duration: "15s", resolution: "1920×1080" },
    output: "✓ Passed · Generating... ✓ kling-3.0 → 1920×1080 h264",
    color: C.green,
    icon: "05",
  },
];

const ToolCallCard: React.FC<{ call: ToolCall; isActive: boolean; progress: number; index: number; totalCalls: number }> = ({
  call,
  isActive,
  progress,
  index,
  totalCalls,
}) => {
  const frame = useCurrentFrame();

  // Card entrance
  const cardY = spring({
    frame: isActive ? frame : 0,
    fps: FPS,
    from: 60,
    to: 0,
    durationInFrames: 18,
    config: { damping: 18, stiffness: 160 },
  });
  const cardOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  // Typing animation for input
  const inputEntries = Object.entries(call.input);
  const lines: string[] = [];
  inputEntries.forEach(([k, v]) => {
    lines.push(`  ${k}: ${v}`);
  });

  // Progress bar
  const barWidth = isActive ? interpolate(progress, [0, 1], [0, 100], { extrapolateRight: "clamp" }) : 100;

  // Output reveal
  const outputOpacity = isActive ? interpolate(progress, [0.6, 0.85], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;

  if (!isActive && progress < 1) return null;

  return (
    <div
      style={{
        opacity: cardOpacity,
        transform: `translateY(${cardY}px)`,
        backgroundColor: C.cardBg,
        border: `1px solid ${isActive ? call.color + "40" : C.terminalBorder}`,
        borderRadius: 8,
        padding: "20px 28px",
        marginBottom: 12,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Active glow */}
      {isActive && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 2,
            backgroundColor: call.color,
            boxShadow: `0 0 12px ${call.color}`,
            width: `${barWidth}%`,
          }}
        />
      )}

      {/* Tool name + step number */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 6,
            backgroundColor: call.color + "20",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Mono color={call.color} size={13} weight={600}>{call.icon}</Mono>
        </div>
        <Mono color={call.color} size={18} weight={600}>{call.tool}</Mono>
        {isActive && (
          <Mono color={C.dim} size={12} style={{ marginLeft: "auto" }}>
            {Math.round(progress * 100)}%
          </Mono>
        )}
        {!isActive && progress >= 1 && (
          <Mono color={C.green} size={14} style={{ marginLeft: "auto" }}>done</Mono>
        )}
      </div>

      {/* Input params */}
      <div style={{ marginBottom: 10 }}>
        {inputEntries.map(([k, v], i) => (
          <div key={k} style={{ display: "flex", gap: 8, lineHeight: 1.6 }}>
            <Mono color={C.dim} size={13}>{k}:</Mono>
            <Mono color={C.text} size={13} style={{ maxWidth: 700 }}>{v}</Mono>
          </div>
        ))}
      </div>

      {/* Output */}
      <div style={{ opacity: outputOpacity, borderTop: `1px solid ${C.terminalBorder}`, paddingTop: 10 }}>
        <Mono color={C.green} size={13}>{call.output}</Mono>
      </div>
    </div>
  );
};

const ScenePipeline: React.FC = () => {
  const frame = useCurrentFrame();
  const totalDur = PIPELINE_DUR;

  // Each tool call gets an equal time window
  const callDuration = 130; // frames per tool call (~4.3s each)
  const stagger = 100;      // overlap between calls

  // Header
  const headerOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const headerLine = interpolate(frame, [15, 45], [0, 200], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut });

  // Connection line between cards
  const lineProgress = interpolate(frame, [30, totalDur - 60], [0, TOOL_CALLS.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      {/* Left: Title + connection */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 60,
          width: 260,
          height: "calc(100% - 120px)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <FadeIn delay={0} duration={15}>
          <Mono color="#fff" size={32} weight={700}>Pipeline</Mono>
        </FadeIn>
        <div
          style={{
            width: headerLine,
            height: 2,
            backgroundColor: C.accent,
            marginTop: 12,
            marginBottom: 30,
            boxShadow: "0 0 8px rgba(167, 139, 250, 0.3)",
          }}
        />
        <FadeIn delay={30} duration={15}>
          <Mono color={C.dim} size={14} style={{ lineHeight: 1.8 }}>
            Each tool is an MCP call.
            <br />
            AuteurLayer enriches every shot
            <br />
            with weighted DP profiles.
            <br />
            <br />
            Sanitiser enforces constraints
            <br />
            before generation.
          </Mono>
        </FadeIn>

        {/* Step indicators on left */}
        <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
          {TOOL_CALLS.map((call, i) => {
            const callStart = 40 + i * (callDuration - stagger);
            const callEnd = callStart + callDuration;
            const isDone = frame >= callEnd;
            const isActive = frame >= callStart && frame < callEnd;
            const opacity = interpolate(frame, [callStart, callStart + 10], [0.3, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, opacity }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    backgroundColor: isDone ? C.green : isActive ? call.color : C.dim,
                    boxShadow: isActive ? `0 0 8px ${call.color}` : "none",
                  }}
                />
                <Mono color={isDone ? C.green : isActive ? call.color : C.dim} size={11}>{call.tool}</Mono>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right: Tool call cards */}
      <div
        style={{
          position: "absolute",
          left: 380,
          right: 60,
          top: 60,
          bottom: 60,
          overflow: "hidden",
        }}
      >
        {TOOL_CALLS.map((call, i) => {
          const callStart = 40 + i * (callDuration - stagger);
          const callEnd = callStart + callDuration;
          const isActive = frame >= callStart && frame < callEnd;
          const progress = isActive
            ? interpolate(frame, [callStart, callEnd], [0, 1], { extrapolateRight: "clamp" })
            : frame >= callEnd
              ? 1
              : 0;

          return (
            <ToolCallCard
              key={i}
              call={call}
              isActive={isActive}
              progress={progress}
              index={i}
              totalCalls={TOOL_CALLS.length}
            />
          );
        })}
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ── Scene 5: OUTPUT (43-58s) ──
const SceneOutput: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [420, 450], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // HUD elements stagger in
  const hudOpacity = interpolate(frame, [20, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ opacity: fadeIn }}>
      <OffthreadVideo
        src={staticFile("shot.mp4")}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />

      {/* Fade to black at end */}
      <AbsoluteFill
        style={{
          backgroundColor: "#000",
          opacity: interpolate(frame, [410, 450], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      />

      {/* Top-left: model info */}
      <div
        style={{
          position: "absolute",
          top: 30,
          left: 30,
          opacity: hudOpacity,
          display: "flex",
          gap: 20,
        }}
      >
        {[
          { label: "MODEL", value: "kling-3.0", color: C.blue },
          { label: "DURATION", value: "15.0s", color: C.dim },
          { label: "RESOLUTION", value: "1920×1080", color: C.dim },
        ].map((item, i) => (
          <FadeIn key={i} delay={25 + i * 10} duration={12}>
            <div style={{ backgroundColor: "rgba(0,0,0,0.7)", padding: "10px 16px", borderRadius: 6 }}>
              <Mono color={C.dim} size={10}>{item.label}</Mono>
              <div><Mono color={item.color} size={16} weight={500}>{item.value}</Mono></div>
            </div>
          </FadeIn>
        ))}
      </div>

      {/* Bottom-left: shot metadata */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 40,
          backgroundColor: "rgba(0,0,0,0.7)",
          padding: "18px 24px",
          borderRadius: 6,
          opacity: hudOpacity,
          maxWidth: 520,
        }}
      >
        <div style={{ display: "flex", gap: 24, marginBottom: 10 }}>
          <div>
            <Mono color={C.dim} size={10}>BEAT</Mono>
            <div><Mono color={C.orange} size={16} weight={500}>climax</Mono></div>
          </div>
          <div>
            <Mono color={C.dim} size={10}>TENSION</Mono>
            <div><Mono color={C.red} size={16} weight={500}>0.95</Mono></div>
          </div>
          <div>
            <Mono color={C.dim} size={10}>CAMERA</Mono>
            <div><Mono color={C.text} size={16} weight={500}>ARRI Alexa Mini LF 35mm</Mono></div>
          </div>
        </div>
        <div>
          <Mono color={C.dim} size={10}>MEISNER NOTE</Mono>
          <div style={{ marginTop: 4 }}>
            <Mono color={C.text} size={13}>
              She takes both hands off the wheel and types.
              <br />
              He watches the bikies. Neither of them speaks.
            </Mono>
          </div>
        </div>
      </div>

      {/* Right side: Auteur blend bar chart */}
      <div
        style={{
          position: "absolute",
          top: 30,
          right: 30,
          backgroundColor: "rgba(0,0,0,0.7)",
          padding: "18px 24px",
          borderRadius: 6,
          opacity: hudOpacity,
          width: 260,
        }}
      >
        <Mono color={C.dim} size={10} style={{ marginBottom: 14 }}>AUTEUR LAYER</Mono>
        {[
          { name: "Hoytema", pct: 44, color: C.yellow },
          { name: "Lubezki", pct: 14, color: C.blue },
          { name: "Storaro", pct: 12, color: C.purple },
          { name: "Deakins", pct: 29, color: C.green },
        ].map((dp, i) => {
          const barWidth = interpolate(frame, [50 + i * 8, 80 + i * 8], [0, dp.pct], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: easeOut,
          });
          return (
            <div key={i} style={{ marginBottom: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                <Mono color={dp.color} size={11}>{dp.name}</Mono>
                <Mono color={C.dim} size={11}>{dp.pct}%</Mono>
              </div>
              <div style={{ height: 4, backgroundColor: "#1a1a2e", borderRadius: 2 }}>
                <div
                  style={{
                    width: `${barWidth}%`,
                    height: "100%",
                    backgroundColor: dp.color,
                    borderRadius: 2,
                    boxShadow: `0 0 6px ${dp.color}40`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 6: ONCHAIN (58-76s) ──
const ONCHAIN_STEPS = [
  { label: "HTTP 402 — Payment Required", detail: "amount: 0.0001 ETH · chain: base-sepolia", color: C.orange, icon: "⟐" },
  { label: "EIP-712 Signature", detail: "signer: 0xBAc0...2109 · nonce: 84721", color: C.blue, icon: "⌘" },
  { label: "x402 Verify", detail: "signature valid · nonce fresh · expiry OK", color: C.green, icon: "✓" },
  { label: "spend() — auteur.sol", detail: "0x4473...fdE3 · emits SpendReceipt", color: C.purple, icon: "⬡" },
  { label: "IPFS Pin", detail: "image CID: QmNsWukw... · metadata CID: QmNSGw...", color: C.blue, icon: "◉" },
  { label: "Rare Protocol Mint", detail: "Token #1 · ShotNFT: 0x24D2...f126", color: C.yellow, icon: "◆" },
];

const SceneOnchain: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [510, 540], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const stepDuration = 75;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, opacity: fadeIn * fadeOut }}>
      {/* Left: header */}
      <div style={{ position: "absolute", left: 60, top: 60 }}>
        <FadeIn delay={0} duration={15}>
          <Mono color="#fff" size={32} weight={700}>Onchain Settlement</Mono>
        </FadeIn>
        <FadeIn delay={15} duration={15}>
          <div style={{ width: 200, height: 2, backgroundColor: C.accent, marginTop: 12, boxShadow: "0 0 8px rgba(167, 139, 250, 0.3)" }} />
        </FadeIn>
        <FadeIn delay={30} duration={15}>
          <div style={{ marginTop: 20, maxWidth: 260 }}>
            <Mono color={C.dim} size={13} style={{ lineHeight: 1.7 }}>
              Every generation settles onchain.
              x402 payment gate enforces per-call billing.
              Proof of work pinned to IPFS.
              Rare Protocol handles secondary markets.
            </Mono>
          </div>
        </FadeIn>
      </div>

      {/* Center: Animated flow */}
      <div
        style={{
          position: "absolute",
          left: 420,
          right: 60,
          top: 80,
          bottom: 80,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: 0,
        }}
      >
        {ONCHAIN_STEPS.map((step, i) => {
          const start = 20 + i * stepDuration;
          const end = start + stepDuration;
          const isActive = frame >= start && frame < end;
          const isDone = frame >= end;
          const progress = isActive
            ? interpolate(frame, [start, end], [0, 1], { extrapolateRight: "clamp" })
            : isDone ? 1 : 0;

          const opacity = interpolate(frame, [start, start + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const y = interpolate(frame, [start, start + 12], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut });

          // Connector line
          const lineProgress = isDone ? 1 : interpolate(frame, [start + 20, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

          return (
            <div key={i}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  opacity,
                  transform: `translateY(${y}px)`,
                  padding: "14px 0",
                  borderBottom: i < ONCHAIN_STEPS.length - 1 ? `1px solid ${C.terminalBorder}` : "none",
                }}
              >
                {/* Icon circle */}
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    backgroundColor: step.color + "15",
                    border: `1px solid ${step.color}40`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <Mono color={step.color} size={16}>{step.icon}</Mono>
                </div>

                {/* Label + detail */}
                <div style={{ flex: 1 }}>
                  <Mono color={isDone ? C.green : step.color} size={16} weight={500}>{step.label}</Mono>
                  <div style={{ marginTop: 4 }}>
                    <Mono color={C.dim} size={12}>{step.detail}</Mono>
                  </div>
                </div>

                {/* Status */}
                {isActive && (
                  <div
                    style={{
                      width: 40,
                      height: 4,
                      backgroundColor: "#1a1a2e",
                      borderRadius: 2,
                      overflow: "hidden",
                    }}
                  >
                    <div style={{ width: `${progress * 100}%`, height: "100%", backgroundColor: step.color, borderRadius: 2 }} />
                  </div>
                )}
                {isDone && <Mono color={C.green} size={13}>✓</Mono>}
              </div>
            </div>
          );
        })}
      </div>

      {/* Right panel: TX hashes */}
      <div
        style={{
          position: "absolute",
          right: 60,
          bottom: 80,
          backgroundColor: C.cardBg,
          border: `1px solid ${C.terminalBorder}`,
          borderRadius: 6,
          padding: "16px 20px",
          opacity: interpolate(frame, [380, 410], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        <Mono color={C.dim} size={10} style={{ marginBottom: 10 }}>TRANSACTION PROOF</Mono>
        {[
          { label: "SpendReceipt", tx: "0x4274b1e2603e5d2b...c639579" },
          { label: "Mint (Token #1)", tx: "0x105b69a889b4cd...4f99ce863" },
          { label: "Bid Recomposition", tx: "0xf5e702a253d4fc...72b97c1d" },
        ].map((item, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <Mono color={C.purple} size={10}>{item.label}</Mono>
            <div><Mono color={C.green} size={11}>{item.tx}</Mono></div>
          </div>
        ))}
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ── Scene 7: RARE PROTOCOL (76-90s) ──
const SceneRare: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [390, 420], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Supply curve animation
  const curveProgress = interpolate(frame, [40, 200], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut });

  // Points on the curve
  const points = [
    { x: 40, y: 380, label: "1.0 ETH", sub: "Token #1" },
    { x: 160, y: 320, label: "1.5 ETH", sub: "Token #2" },
    { x: 320, y: 240, label: "2.8 ETH", sub: "Token #3" },
    { x: 500, y: 160, label: "4.5 ETH", sub: "Token #4" },
    { x: 650, y: 100, label: "7.2 ETH", sub: "Token #5" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, opacity: fadeIn * fadeOut }}>
      <div style={{ position: "absolute", left: 60, top: 60 }}>
        <FadeIn delay={0} duration={15}>
          <Mono color="#fff" size={32} weight={700}>Rare Protocol</Mono>
        </FadeIn>
        <FadeIn delay={10} duration={15}>
          <Mono color={C.yellow} size={18}>Dynamic pricing for AI-generated art</Mono>
        </FadeIn>
        <FadeIn delay={20} duration={15}>
          <div style={{ width: 300, height: 2, backgroundColor: C.yellow, marginTop: 12, boxShadow: "0 0 8px rgba(250, 204, 21, 0.3)" }} />
        </FadeIn>
      </div>

      {/* Supply curve chart */}
      <div
        style={{
          position: "absolute",
          left: 100,
          top: 160,
          width: 760,
          height: 440,
          borderLeft: `1px solid ${C.terminalBorder}`,
          borderBottom: `1px solid ${C.terminalBorder}`,
        }}
      >
        {/* Y axis */}
        <FadeIn delay={30} duration={15}>
          <Mono color={C.dim} size={11} style={{ position: "absolute", top: -20, left: -60 }}>PRICE (ETH)</Mono>
        </FadeIn>
        {/* X axis */}
        <FadeIn delay={35} duration={15}>
          <Mono color={C.dim} size={11} style={{ position: "absolute", bottom: -24, right: 0 }}>TOKEN SUPPLY</Mono>
        </FadeIn>

        {/* Grid lines */}
        {[0, 100, 200, 300, 400].map((y) => (
          <div key={y} style={{ position: "absolute", top: y, left: 0, right: 0, height: 0, borderTop: "1px solid #161622" }} />
        ))}

        {/* Curve path - animated SVG */}
        <svg
          style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
          viewBox="0 0 760 440"
        >
          {/* Animated curve */}
          <path
            d={`M 0,420 Q ${curveProgress * 200},400 ${curveProgress * 400},280 Q ${curveProgress * 550},180 ${curveProgress * 750},40`}
            fill="none"
            stroke={C.yellow}
            strokeWidth={2}
            strokeDasharray="4 4"
            opacity={0.6}
          />
          {/* Solid fill underneath */}
          <path
            d={`M 0,420 Q ${curveProgress * 200},400 ${curveProgress * 400},280 Q ${curveProgress * 550},180 ${curveProgress * 750},40 L ${curveProgress * 750},420 Z`}
            fill={`${C.yellow}08`}
            stroke="none"
          />
        </svg>

        {/* Data points */}
        {points.map((pt, i) => {
          const ptProgress = interpolate(frame, [80 + i * 30, 120 + i * 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const scale = spring({ frame: Math.max(0, frame - 80 - i * 30), fps: FPS, from: 0, to: 1, durationInFrames: 10, config: { damping: 12, stiffness: 200 } });

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: pt.x,
                top: pt.y * ptProgress + (1 - ptProgress) * 420,
                opacity: ptProgress,
              }}
            >
              <div
                style={{
                  width: 10 * scale,
                  height: 10 * scale,
                  borderRadius: "50%",
                  backgroundColor: C.yellow,
                  boxShadow: `0 0 12px ${C.yellow}`,
                  marginTop: -5,
                  marginLeft: -5,
                }}
              />
              <div style={{ position: "absolute", top: -40, left: 10, opacity: ptProgress }}>
                <Mono color={C.yellow} size={12} weight={500}>{pt.label}</Mono>
                <div><Mono color={C.dim} size={10}>{pt.sub}</Mono></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Right side: Features */}
      <div
        style={{
          position: "absolute",
          right: 60,
          top: 160,
          width: 340,
          display: "flex",
          flexDirection: "column",
          gap: 24,
        }}
      >
        {[
          { title: "ERC-721 Shots", desc: "Every generated video minted as an onchain asset with full metadata provenance." },
          { title: "Bonding Curve", desc: "Automated price discovery. No auctions. No floor wars. Pure bonding curve mechanics." },
          { title: "Bid Recomposition", desc: "Collectors can re-mint shots with new parameters. The original creator earns royalties." },
        ].map((f, i) => (
          <FadeIn key={i} delay={200 + i * 40} duration={15}>
            <div style={{ borderLeft: `2px solid ${C.yellow}`, paddingLeft: 16 }}>
              <Mono color={C.yellow} size={15} weight={500}>{f.title}</Mono>
              <div style={{ marginTop: 6 }}>
                <Mono color={C.dim} size={12} style={{ lineHeight: 1.6 }}>{f.desc}</Mono>
              </div>
            </div>
          </FadeIn>
        ))}
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ── Scene 8: CLOSE (90-105s) ──
const SceneClose: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: "clamp" });
  const titleScale = spring({ frame, fps: FPS, from: 0.96, to: 1, durationInFrames: 25, config: { damping: 15, stiffness: 120 } });

  const lines = [
    { text: "14 MCP tools · 4 DP profiles · x402 payments · Rare Protocol", delay: 60, color: C.accent },
    { text: "The README is the interface.", delay: 110, color: C.dim },
    { text: "Every frame verified. Every shot onchain.", delay: 160, color: C.dim },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <div style={{ opacity: titleOpacity, transform: `scale(${titleScale})` }}>
          <Mono color="#fff" size={100} weight={700}>0xAUTEUR</Mono>
        </div>

        <div style={{ marginTop: 50, display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
          {lines.map((line, i) => (
            <FadeIn key={i} delay={line.delay} duration={15}>
              <Mono color={line.color} size={20}>{line.text}</Mono>
            </FadeIn>
          ))}
        </div>

        <FadeIn delay={220} duration={15}>
          <div style={{ marginTop: 60, display: "flex", gap: 30 }}>
            <Mono color={C.blue} size={18}>Base</Mono>
            <Mono color={C.dim} size={18}>·</Mono>
            <Mono color={C.yellow} size={18}>Rare Protocol</Mono>
            <Mono color={C.dim} size={18}>·</Mono>
            <Mono color={C.green} size={18}>ERC-8183</Mono>
            <Mono color={C.dim} size={18}>·</Mono>
            <Mono color={C.purple} size={18}>x402</Mono>
          </div>
        </FadeIn>
      </div>

      {/* Fade to black */}
      <AbsoluteFill
        style={{
          backgroundColor: "#000",
          opacity: interpolate(frame, [400, 450], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      />
      <Grain />
    </AbsoluteFill>
  );
};

// ── Main Composition ──
export const DemoVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      <Series>
        <Series.Sequence durationInFrames={HOOK_DUR}>
          <SceneHook />
        </Series.Sequence>
        <Series.Sequence durationInFrames={PROBLEM_DUR}>
          <SceneProblem />
        </Series.Sequence>
        <Series.Sequence durationInFrames={THESIS_DUR}>
          <SceneThesis />
        </Series.Sequence>
        <Series.Sequence durationInFrames={PIPELINE_DUR}>
          <ScenePipeline />
        </Series.Sequence>
        <Series.Sequence durationInFrames={OUTPUT_DUR}>
          <SceneOutput />
        </Series.Sequence>
        <Series.Sequence durationInFrames={ONCHAIN_DUR}>
          <SceneOnchain />
        </Series.Sequence>
        <Series.Sequence durationInFrames={RARE_DUR}>
          <SceneRare />
        </Series.Sequence>
        <Series.Sequence durationInFrames={CLOSE_DUR}>
          <SceneClose />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
