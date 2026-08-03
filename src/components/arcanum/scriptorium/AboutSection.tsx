"use client";

import { motion } from "framer-motion";

export default function AboutSection() {
  return (
    <section 
      className="relative py-24 md:py-32 min-h-screen overflow-hidden"
      aria-label="About section"
    >
      {/* Content */}
      <div className="relative z-10 mx-auto max-w-4xl px-4 md:px-8">
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
  );
}
