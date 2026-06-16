"use client";

import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import Lenis from "lenis";
import Navigation from "@/components/arcanum/Navigation";
import HeroSection from "@/components/arcanum/hero/HeroSection";
import AboutSection from "@/components/arcanum/scriptorium/AboutSection";
import GallerySection from "@/components/arcanum/gallery/GallerySection";
import ConScheduleSection from "@/components/arcanum/ConScheduleSection";
import ContactSection from "@/components/arcanum/ContactSection";
import FooterSection from "@/components/arcanum/footer/FooterSection";

/* ─── Floating mana particle ─── */
function ManaParticle({ delay, color, size, left }: { delay: number; color: string; size: number; left: string }) {
  return (
    <motion.div
      className="absolute rounded-full pointer-events-none"
      style={{ 
        left, 
        width: size, 
        height: size, 
        backgroundColor: color,
        boxShadow: `0 0 ${size * 2}px ${color}`,
        filter: `blur(${size / 3}px)`
      }}
      initial={{ bottom: "-5%", opacity: 0, scale: 0 }}
      animate={{ 
        bottom: "105%", 
        opacity: [0, 1, 1, 0],
        scale: [0, 1, 0.5, 0],
        x: [0, 20, -20, 0]
      }}
      transition={{ 
        duration: 8 + Math.random() * 4, 
        repeat: Infinity, 
        delay, 
        ease: "easeOut" 
      }}
    />
  );
}

/* ─── Energy orb background ─── */
function EnergyOrb({ color, className, blur = 100 }: { color: string; className: string; blur?: number }) {
  return (
    <motion.div
      className={`absolute rounded-full pointer-events-none ${className}`}
      style={{ background: color, filter: `blur(${blur}px)` }}
      animate={{ 
        x: [0, 50, -30, 0], 
        y: [0, -60, 40, 0],
        scale: [1, 1.2, 0.9, 1]
      }}
      transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
    />
  );
}

export default function Home() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true,
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    setIsMobile(mq.matches);
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const particles = useMemo(() =>
    Array.from({ length: isMobile ? 25 : 40 }, (_, i) => ({
      id: i,
      delay: Math.random() * 10,
      color: ["#c2ac7b", "#1e6b8a", "#d4a373", "#0d4a6b", "#d49a1a"][Math.floor(Math.random() * 5)],
      size: isMobile ? 1.5 + Math.random() * 3 : 2 + Math.random() * 6,
      left: `${Math.random() * 100}%`
    })),
    [isMobile]
  );

  return (
    <div className="relative overflow-x-hidden">
      {/* ═══════ Mana Particles + Energy Orbs Layer ═══════ */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden w-full h-full">
        {particles.map((p) => (
          <ManaParticle key={p.id} {...p} />
        ))}

        {/* ═══════ Energy Orbs ═══════ */}
        <EnergyOrb color="rgba(194, 172, 123, 0.15)" className="w-[250px] h-[250px] md:w-[600px] md:h-[600px] -top-10 md:-top-40 -left-10 md:-left-40" blur={isMobile ? 40 : 100} />
        <EnergyOrb color="rgba(30, 107, 138, 0.12)" className="w-[200px] h-[200px] md:w-[500px] md:h-[500px] top-[20%] -right-10 md:-right-40" blur={isMobile ? 40 : 100} />
        <EnergyOrb color="rgba(212, 163, 115, 0.1)" className="w-[150px] h-[150px] md:w-[400px] md:h-[400px] top-[40%] md:top-[60%] left-[5%] md:left-[20%]" blur={isMobile ? 30 : 100} />
        <EnergyOrb color="rgba(139, 0, 0, 0.08)" className="w-[150px] h-[150px] md:w-[350px] md:h-[350px] bottom-[5%] md:bottom-[10%] right-[10%] md:right-[30%]" blur={isMobile ? 30 : 100} />
      </div>

      <Navigation />
      
      <main className="relative flex flex-col">
        {/* Hero Section - The Storm-Crowned Castle */}
        <div id="hero">
          <HeroSection />
        </div>

        {/* About Section - The Scriptorium */}
        <div id="about">
          <AboutSection />
        </div>

        {/* Gallery Section - The Reliquary */}
        <div id="gallery">
          <GallerySection />
        </div>

        {/* Con Schedule Section - The Caravan */}
        <div id="events">
          <ConScheduleSection />
        </div>

        {/* Contact Section - The Royal Decree */}
        <div id="contact">
          <ContactSection />
        </div>

        {/* Footer - The Vampiric Void */}
        <FooterSection />
      </main>
    </div>
  );
}
