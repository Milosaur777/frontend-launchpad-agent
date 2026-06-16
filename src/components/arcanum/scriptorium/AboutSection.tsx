"use client";

import { motion } from "framer-motion";

export default function AboutSection() {
  return (
    <section 
      className="relative py-24 md:py-32 min-h-screen bg-storm-void overflow-hidden"
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
            <div className="absolute top-[45%] left-1/2 -translate-x-1/2 w-[75%] md:w-[70%] text-center">
              <p className="font-cormorant text-base md:text-lg leading-relaxed text-parchment-ink/90">
                I am a digital artist and worldbuilder passionate about art, games and the stories that linger in forgotten places.
              </p>
              <p className="font-cormorant text-base md:text-lg leading-relaxed text-parchment-ink/90 mt-4">
                Through light, shadow, I strive to evoke emotion and mystery, inviting you to step into realms where imagination and darkness entwine.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Decorative divider */}
        <div className="flex items-center justify-center gap-4 my-16">
          <div className="relative w-24 h-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
          <svg className="w-8 h-8 text-parchment-gold/40" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L15 9L22 9L16 14L18 21L12 17L6 21L8 14L2 9L9 9L12 2Z" />
          </svg>
          <div className="relative w-24 h-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
