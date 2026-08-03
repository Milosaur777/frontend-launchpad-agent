"use client";

import { motion } from "framer-motion";
import Navigation from "@/components/arcanum/Navigation";

export default function AboutPage() {
  return (
    <div className="relative overflow-x-hidden">
      <Navigation />
      <main className="relative flex flex-col">
        <section
          className="relative py-24 md:py-32 min-h-screen overflow-hidden"
          aria-label="About section"
        >
          <div className="relative z-10 mx-auto max-w-4xl px-4 md:px-8">
            {/* Section Header */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="inline-flex items-center gap-2 rounded-full bg-storm-void px-4 py-2 border border-parchment-gold/30 mb-6">
                <span className="text-sm font-semibold text-storm-moon">About</span>
              </div>
              <h1 className="font-exocet text-4xl md:text-5xl text-storm-moon mb-4 subtitle-pulse">
                The Scriptorium
              </h1>
              <div className="relative w-48 md:w-64 h-6 mx-auto mb-4">
                <img
                  src="/images/line-separator.avif"
                  alt="Decorative divider"
                  className="w-full h-full object-contain"
                />
              </div>
              <p className="font-cormorant text-lg text-storm-moon/70 max-w-xl mx-auto">
                The artist behind the Arcanum.
              </p>
            </motion.div>

            {/* Parchment with integrated design */}
            <motion.div
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
              className="relative"
            >
              {/* Parchment background image */}
              <div className="relative w-full">
                <img
                  src="/images/parchment-new-mobile.avif"
                  alt="Parchment scroll"
                  className="w-full h-auto"
                />

                {/* Text overlay positioned on the parchment */}
                <div className="absolute top-[60px] left-1/2 -translate-x-1/2 w-[70%] md:w-[60%] text-center">
                  <p className="font-blackletter text-[16px] md:text-[26px] leading-snug text-parchment-ink md:text-[#8b0000]">
                    Hi, I'm Milo
                  </p>
                  <p className="font-blackletter text-[13px] md:text-[22px] leading-snug text-parchment-ink md:text-[#8b0000] mt-4">
                    I'm a digital artist, full-stack developer and lifelong creator with a passion for sci-fi, games, anime and music.
                  </p>
                  <p className="font-blackletter text-[13px] md:text-[22px] leading-snug text-parchment-ink md:text-[#8b0000] mt-4">
                    For the past several years I've been building web applications, workflow automations for businesses. I enjoy solving complex problems and turning ambitious ideas into polished products.
                  </p>
                  <p className="font-blackletter text-[13px] md:text-[22px] leading-snug text-parchment-ink md:text-[#8b0000] mt-4">
                    Outside of client work, I love building passion projects that combine technology with creativity. One of those projects is Unhinged, a dating platform designed specifically for role-players to meet in-character, discover new stories, and connect with like-minded people.
                  </p>
                  <p className="font-blackletter text-[13px] md:text-[22px] leading-snug text-parchment-ink md:text-[#8b0000] mt-4">
                    Welcome to my world.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
    </div>
  );
}
