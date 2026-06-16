"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

import Image from "next/image";

export default function HeroSection() {
  const heroRef = useRef<HTMLDivElement>(null);
  const mistRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let targetScrollY = 0;
    let currentScrollY = 0;
    let rafId: number;
    
    const handleScroll = () => {
      targetScrollY = window.scrollY;
    };
    
    const animate = () => {
      if (!heroRef.current || !mistRef.current || !imageRef.current) {
        rafId = requestAnimationFrame(animate);
        return;
      }
      
      // Smooth interpolation (lerp) for buttery scroll
      const ease = 0.08;
      currentScrollY += (targetScrollY - currentScrollY) * ease;
      
      const heroHeight = heroRef.current.offsetHeight;
      const progress = Math.min(currentScrollY / heroHeight, 1);
      
      // Parallax effect for mist layers
      const mistLayers = mistRef.current.querySelectorAll(".mist-layer");
      mistLayers.forEach((layer, index) => {
        const speed = (index + 1) * 0.3;
        (layer as HTMLElement).style.transform = `translateY(${currentScrollY * speed}px)`;
        (layer as HTMLElement).style.opacity = `${1 - progress * 0.8}`;
      });
      
      // Parallax effect for castle image - only vertical movement, no scale
      imageRef.current.style.transform = `translateY(${currentScrollY * 0.15}px)`;
      imageRef.current.style.opacity = `${1 - progress * 0.5}`;
      
      rafId = requestAnimationFrame(animate);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    rafId = requestAnimationFrame(animate);
    
    return () => {
      window.removeEventListener("scroll", handleScroll);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative h-screen w-full overflow-hidden bg-storm-void"
      aria-label="Hero section - Storm crowned castle"
    >
      {/* Storm Sky Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-storm-void via-storm-mist to-storm-void">
        {/* Cloud layers */}
        <div className="absolute inset-0 opacity-40">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-storm-cloud/20 via-transparent to-storm-cloud/30" />
        </div>
      </div>

      {/* Castle Image Background */}
      <div
        ref={imageRef}
        className="absolute inset-0 w-full h-full transition-transform will-change-transform"
      >
        {/* Desktop castle image */}
        <Image
          src="/images/hero-castle.avif"
          alt="Dark fantasy castle on a cliff during a stormy night with a full moon"
          fill
          priority
          className="object-cover object-center hidden md:block"
          sizes="100vw"
        />
        {/* Mobile castle image */}
        <Image
          src="/images/hero-castle-mobile.avif"
          alt="Dark fantasy castle on a cliff during a stormy night with a full moon"
          fill
          priority
          className="object-cover object-center md:hidden"
          sizes="100vw"
        />
        {/* Dark overlay to ensure text readability - lighter on mobile */}
        <div className="absolute top-0 left-0 right-0 bottom-0 w-screen min-w-full bg-gradient-to-t from-storm-void via-storm-void/30 to-storm-void/50 md:via-storm-void/40 md:to-storm-void/60" />
        {/* Bottom gradient for smooth transition */}
        <div className="absolute bottom-0 left-0 right-0 w-screen min-w-full h-48 bg-gradient-to-t from-storm-void to-transparent" />
      </div>

      {/* Mist layers */}
      <div ref={mistRef} className="absolute inset-0 pointer-events-none" aria-hidden="true">
        {/* Mist layer 1 - foreground */}
        <div className="mist-layer absolute bottom-0 left-0 w-[calc(100%+80px)] -left-[40px] h-48 md:h-64 bg-gradient-to-t from-storm-void/80 via-storm-mist/40 to-transparent mist-drift" />
        
        {/* Mist layer 2 - midground */}
        <div className="mist-layer absolute bottom-20 left-0 w-[calc(100%+80px)] -left-[40px] h-32 md:h-48 bg-gradient-to-t from-storm-void/60 via-storm-cloud/30 to-transparent mist-drift-slow" />
        
        {/* Mist layer 3 - background */}
        <div className="mist-layer absolute bottom-40 left-0 w-[calc(100%+80px)] -left-[40px] h-24 md:h-32 bg-gradient-to-t from-storm-mist/40 via-storm-cloud/20 to-transparent mist-drift-fast" />
        
        {/* Floating mist particles */}
        <div className="mist-layer absolute top-1/3 left-1/4 w-32 h-32 rounded-full bg-storm-cloud/10 blur-3xl mist-drift" />
        <div className="mist-layer absolute top-1/2 right-1/4 w-48 h-48 rounded-full bg-storm-mist/10 blur-3xl mist-drift-slow" />
        <div className="mist-layer absolute top-1/4 left-1/2 w-24 h-24 rounded-full bg-storm-cloud/15 blur-2xl mist-drift-fast" />
      </div>

      {/* Hero Text Content */}
      <div className="absolute inset-0 flex flex-col items-center justify-end pb-24 md:pb-32 z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.5, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="text-center"
        >
          <h1 className="font-exocet text-5xl md:text-7xl lg:text-8xl text-storm-moon text-glow-gold mb-4 title-pulse">
            Milo&apos;s Arcanum
          </h1>
          <p className="font-cinzel text-lg md:text-xl text-storm-moon/80 tracking-widest uppercase mb-2">
            Welcome To My Art Gallery
          </p>
          <div className="relative w-48 md:w-64 h-6 mx-auto mb-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
          <p className="font-cormorant text-base md:text-lg text-storm-moon/60 italic max-w-md mx-auto px-4">
            &ldquo;Where the storm meets the scriptorium, and the void beyond whispers secrets...&rdquo;
          </p>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
          className="mt-8 flex flex-col items-center gap-2"
        >
          <span className="font-cinzel text-xs text-storm-moon/50 tracking-widest uppercase">
            Enter Here
          </span>
          <div className="scroll-bounce">
            <img
              src="/images/arrow-down.avif"
              alt="Scroll down"
              className="w-6 h-6 md:w-8 md:h-8 object-contain"
            />
          </div>
        </motion.div>
      </div>

      {/* Bottom gradient transition to dark */}
      <div className="absolute bottom-0 left-0 right-0 w-screen min-w-full h-32 bg-gradient-to-t from-storm-void to-transparent pointer-events-none" />
    </section>
  );
}
