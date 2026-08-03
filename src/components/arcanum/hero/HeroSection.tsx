"use client";

import { useEffect, useRef, useState } from "react";

import { motion } from "framer-motion";

import Image from "next/image";

export default function HeroSection() {
  const desktopVideoRef = useRef<HTMLVideoElement>(null);
  const mobileVideoRef = useRef<HTMLVideoElement>(null);
  const [videoVisible, setVideoVisible] = useState(false);

  useEffect(() => {
    const desktopVideo = desktopVideoRef.current;
    const mobileVideo = mobileVideoRef.current;

    // Slow down by 25%
    if (desktopVideo) desktopVideo.playbackRate = 0.75;
    if (mobileVideo) mobileVideo.playbackRate = 0.75;

    // Explicit play attempt — helps when the browser blocks autoplay on refresh
    [desktopVideo, mobileVideo].forEach((video) => {
      if (!video) return;
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          // Autoplay blocked: static image underneath stays visible
        });
      }
    });

    // Reveal the video quickly with a 4-second fade.
    // The static image underneath ensures the hero is never blank.
    // Small delay (100ms) lets the first frame render before fading begins.
    const timer = setTimeout(() => {
      setVideoVisible(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <section
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

      {/* Castle Background */}
      <div className="absolute inset-0 w-full h-full z-[1]">
        {/* Mobile static image */}
        <Image
          src="/images/hero-castle-mobile.avif"
          alt="Dark fantasy castle on a cliff during a stormy night with a full moon"
          fill
          priority
          className="object-cover object-center md:hidden"
          sizes="100vw"
        />

        {/* Desktop static image — bottom layer, visible while the video loads */}
        <Image
          src="/images/hero-castle.avif"
          alt="Dark fantasy castle on a cliff during a stormy night with a full moon"
          fill
          priority
          className="object-cover object-center hidden md:block"
          sizes="100vw"
        />

        {          /*
          Looping video background.
          Mobile and desktop have separate videos with correct aspect ratios.
          Rendered AFTER the static image so it stacks on top.
          Fades in smoothly over 4 seconds. Hidden only on reduced motion.
        */}

        {/* Desktop video */}
        <video
          ref={desktopVideoRef}
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          poster="/images/hero-castle.avif"
          disablePictureInPicture
          disableRemotePlayback
          aria-hidden="true"
          className={`hidden md:block motion-reduce:hidden absolute inset-0 w-full h-full object-cover object-center transition-opacity ease-out ${videoVisible ? "opacity-100" : "opacity-0"}`}
          style={{ transitionDuration: "4000ms" }}
        >
          <source src="/videos/hero-castle.webm" type="video/webm" />
          <source src="/videos/hero-castle.mp4" type="video/mp4" />
        </video>

        {/* Mobile video — portrait aspect ratio, pre-aligned */}
        <video
          ref={mobileVideoRef}
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          poster="/images/hero-castle-mobile.avif"
          disablePictureInPicture
          disableRemotePlayback
          aria-hidden="true"
          className={`block md:hidden motion-reduce:hidden absolute inset-0 w-full h-full object-cover object-top transition-opacity ease-out ${videoVisible ? "opacity-100" : "opacity-0"}`}
          style={{ transitionDuration: "4000ms" }}
        >
          <source src="/videos/hero-castle-mobile.webm" type="video/webm" />
          <source src="/videos/hero-castle-mobile.mp4" type="video/mp4" />
        </video>

        {/* Dark overlay to ensure text readability - lighter on mobile */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[200vw] h-full bg-gradient-to-t from-storm-void/70 via-storm-void/20 to-storm-void/40 md:from-storm-void md:via-storm-void/40 md:to-storm-void/60" />
        {/* Bottom gradient for smooth transition */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[200vw] h-48 bg-gradient-to-t from-storm-void to-transparent" />
      </div>

      {/* Mist layers */}
      <div className="absolute inset-0 pointer-events-none z-[5]" aria-hidden="true">
        {/* Mist layer 1 - foreground: fades in from bottom AND top on mobile */}
        <div className="mist-layer absolute bottom-[110px] md:bottom-[-20px] left-1/2 -translate-x-1/2 w-[220vw] md:w-[200vw] h-32 md:h-64 bg-gradient-to-t from-transparent via-storm-mist/40 to-transparent md:via-storm-mist/40 mist-drift animate-fade-in" />
        
        {/* Mist layer 2 - midground */}
        <div className="mist-layer absolute bottom-[135px] md:bottom-[60px] left-1/2 -translate-x-1/2 w-[220vw] md:w-[200vw] h-24 md:h-48 bg-gradient-to-t from-transparent via-storm-cloud/30 to-transparent md:via-storm-cloud/30 mist-drift-slow animate-fade-in" />
        
        {/* Mist layer 3 - background */}
        <div className="mist-layer absolute bottom-[165px] md:bottom-[140px] left-1/2 -translate-x-1/2 w-[220vw] md:w-[200vw] h-16 md:h-32 bg-gradient-to-t from-transparent via-storm-cloud/20 to-transparent md:via-storm-cloud/20 mist-drift-fast animate-fade-in" />
        
        {/* Floating mist particles */}
        <div className="mist-layer absolute top-1/3 left-1/4 w-32 h-32 rounded-full bg-storm-cloud/20 md:bg-storm-cloud/10 blur-3xl mist-drift" />
        <div className="mist-layer absolute top-1/2 right-1/4 w-48 h-48 rounded-full bg-storm-mist/20 md:bg-storm-mist/10 blur-3xl mist-drift-slow" />
        <div className="mist-layer absolute top-1/4 left-1/2 w-24 h-24 rounded-full bg-storm-cloud/25 md:bg-storm-cloud/15 blur-2xl mist-drift-fast" />
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
            Everything I make is something I once wished existed.
          </p>
        </motion.div>

        {/* Scroll Indicator — click to jump to Gallery */}
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
          onClick={() =>
            document
              .querySelector("#gallery")
              ?.scrollIntoView({ behavior: "smooth" })
          }
          className="mt-8 flex flex-col items-center gap-2 cursor-pointer group"
          aria-label="Scroll to gallery"
        >
          <span className="font-cinzel text-sm text-storm-moon/50 tracking-widest uppercase enter-glow-pulse group-hover:text-parchment-gold transition-all duration-300">
            Enter Here
          </span>
          <div className="scroll-bounce group-hover:drop-shadow-[0_0_8px_rgba(212,154,26,0.6)] transition-all duration-300">
            <img
              src="/images/arrow-down.avif"
              alt="Scroll down"
              className="w-6 h-6 md:w-8 md:h-8 object-contain"
            />
          </div>
        </motion.button>
      </div>

      {/* Bottom gradient transition to dark */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[200vw] h-32 bg-gradient-to-t from-storm-void to-transparent pointer-events-none" />
    </section>
  );
}
