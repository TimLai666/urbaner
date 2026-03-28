import { useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { Icon } from "@iconify/react";
import gsap from "gsap";
import anime from "animejs";
import HeroCanvas from "./components/HeroCanvas";

const cards = [
  { icon: "solar:bolt-bold", title: "{{value_prop_1}}", desc: "高可讀資訊階層，加速理解。" },
  { icon: "solar:shield-check-bold", title: "{{value_prop_2}}", desc: "降低風險感，提升信任與行動意願。" },
  { icon: "solar:rocket-bold", title: "{{value_prop_3}}", desc: "結構化敘事，強化 CTA 轉換。" },
];

export default function App() {
  const reduced = useMemo(
    () => window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    []
  );

  useEffect(() => {
    if (reduced) return;

    gsap.fromTo(
      "[data-reveal]",
      { opacity: 0, y: 22 },
      { opacity: 1, y: 0, duration: 0.8, stagger: 0.08, ease: "power2.out" }
    );

    anime({
      targets: ".hero-glow",
      translateY: [0, -18],
      direction: "alternate",
      loop: true,
      easing: "easeInOutSine",
      duration: 2800,
    });
  }, [reduced]);

  return (
    <div className="min-h-screen bg-bg text-white font-body">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-black/25 backdrop-blur-md">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="font-display text-2xl">{{brand_name}}</span>
          <a className="rounded-full bg-accent px-5 py-2 text-sm font-bold text-slate-900" href="#cta">
            {{primary_cta}}
          </a>
        </nav>
      </header>

      <section className="relative overflow-hidden px-6 pb-20 pt-20">
        <HeroCanvas disabled={reduced} />
        <div className="hero-glow pointer-events-none absolute -top-10 right-0 h-64 w-64 rounded-full bg-cyan-300/20 blur-3xl" />
        <div className="relative mx-auto max-w-6xl">
          <motion.p data-reveal className="mb-3 inline-flex rounded-full border border-cyan-300/70 px-3 py-1 text-xs uppercase tracking-[0.18em] text-cyan-200">
            {{style_variant_label}}
          </motion.p>
          <h1 data-reveal className="max-w-3xl font-display text-4xl leading-tight md:text-6xl">
            {{hero_title}}
          </h1>
          <p data-reveal className="mt-4 max-w-2xl text-lg text-slate-200">
            {{hero_subtitle}}
          </p>
          <div data-reveal className="mt-8 flex gap-4">
            <a href="#cta" className="rounded-full bg-accent px-7 py-3 text-sm font-bold text-slate-900">
              {{primary_cta}}
            </a>
            <a href="#value" className="rounded-full border border-white/50 px-7 py-3 text-sm font-bold">
              了解更多
            </a>
          </div>
        </div>
      </section>

      <section id="value" className="mx-auto grid max-w-6xl gap-6 px-6 pb-20 md:grid-cols-3">
        {cards.map((card) => (
          <motion.article
            key={card.title}
            data-reveal
            whileHover={reduced ? undefined : { y: -6, rotateX: 2, rotateY: -2 }}
            className="glass rounded-2xl p-6"
          >
            <Icon icon={card.icon} width={26} />
            <h3 className="mt-4 text-xl font-bold">{card.title}</h3>
            <p className="mt-2 text-sm text-slate-300">{card.desc}</p>
          </motion.article>
        ))}
      </section>

      <section id="cta" className="mx-auto max-w-6xl px-6 pb-24">
        <motion.div
          data-reveal
          initial={reduced ? false : { opacity: 0, y: 16 }}
          whileInView={reduced ? {} : { opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="beam-border glass rounded-3xl p-10 text-center"
        >
          <h2 className="font-display text-4xl">{{final_cta_title}}</h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-200">{{final_cta_subtitle}}</p>
          <a href="#" className="mt-8 inline-flex rounded-full bg-white px-8 py-3 text-sm font-bold text-slate-900">
            {{primary_cta}}
          </a>
        </motion.div>
      </section>

      <footer className="border-t border-white/10 py-8 text-center text-xs text-slate-400">
        © {{year}} {{brand_name}} · Built with landing-page-studio
      </footer>
    </div>
  );
}
