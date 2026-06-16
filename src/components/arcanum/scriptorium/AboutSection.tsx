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
          className="relative mb-16 md:mx-0 -mx-4"
        >
          {/* Parchment background image */}
          <div className="relative w-full">
            <img
              src="/images/parchment-new-mobile.avif"
              alt="Parchment scroll"
              className="w-full h-auto"
            />

            {/* Text overlay positioned on the parchment */}
            <div className="absolute top-[50px] md:top-[150px] left-1/2 -translate-x-1/2 w-[90%] md:w-[80%] text-center">
              <p className="font-blackletter text-[20px] md:text-[32px] leading-snug text-[#8b0000]">
                I am a digital artist and worldbuilder passionate about art, games and the stories that linger in forgotten places.
              </p>
              <p className="font-blackletter text-[20px] md:text-[32px] leading-snug text-[#8b0000] mt-6">
                Through light, shadow, I strive to evoke emotion and mystery, inviting you to step into realms where imagination and darkness entwine.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
