"use client";

import { useState, useRef } from "react";
import { motion, useInView } from "framer-motion";


export default function ContactSection() {
  const [formState, setFormState] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [isSubmitted, setIsSubmitted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate form submission
    setIsSubmitted(true);
    setTimeout(() => setIsSubmitted(false), 3000);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormState(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <section
      ref={ref}
      className="relative py-24 md:py-32 overflow-hidden"
      aria-label="Contact section - The Royal Decree"
    >

      <div className="relative z-10 mx-auto max-w-4xl px-4 md:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="font-exocet text-3xl md:text-4xl text-storm-moon mb-4 tracking-widest subtitle-pulse">
            The Royal Decree
          </h2>
          <p className="font-cormorant text-lg text-storm-moon/60 italic max-w-lg mx-auto">
            Send a raven to the Keeper of the Arcanum. Commissions, collaborations, and inquiries welcome.
          </p>
          <div className="relative w-48 md:w-64 h-6 mx-auto mt-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
        </motion.div>

        {/* Contact Parchment */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, delay: 0.3 }}
          className="relative"
        >
          {/* Parchment background image */}
          <div className="relative w-full">
            <img
              src="/images/parchment-new-mobile.avif"
              alt="Contact parchment"
              className="w-full h-auto"
            />
            
            {/* Form overlay positioned on the parchment */}
            <div className="absolute top-[35%] left-1/2 -translate-x-1/2 w-[75%] md:w-[70%]">
              <div className="text-center mb-6">
                <h3 className="font-cinzel text-lg md:text-xl text-parchment-ink tracking-widest mb-2">
                  NOTICE OF COMMISSION
                </h3>
                <p className="font-cormorant text-xs text-parchment-ink/60 italic">
                  Order of the Arcanum — Anno Domini 2026
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name field */}
                <div className="relative">
                  <label className="font-cinzel text-[10px] text-parchment-ink/60 tracking-widest uppercase mb-1 block">
                    Name of the Seeker
                  </label>
                  <div className="relative border-b-2 border-parchment-ink/20 focus-within:border-parchment-gold transition-colors">
                    <input
                      type="text"
                      name="name"
                      value={formState.name}
                      onChange={handleChange}
                      required
                      className="w-full bg-transparent py-2 font-cormorant text-base text-parchment-ink placeholder:text-parchment-ink/30 focus:outline-none"
                      placeholder="Enter thy name..."
                    />
                  </div>
                </div>

                {/* Email field */}
                <div className="relative">
                  <label className="font-cinzel text-[10px] text-parchment-ink/60 tracking-widest uppercase mb-1 block">
                    Raven&apos;s Address (Email)
                  </label>
                  <div className="relative border-b-2 border-parchment-ink/20 focus-within:border-parchment-gold transition-colors">
                    <input
                      type="email"
                      name="email"
                      value={formState.email}
                      onChange={handleChange}
                      required
                      className="w-full bg-transparent py-2 font-cormorant text-base text-parchment-ink placeholder:text-parchment-ink/30 focus:outline-none"
                      placeholder="Enter thy correspondence address..."
                    />
                  </div>
                </div>

                {/* Message field */}
                <div className="relative">
                  <label className="font-cinzel text-[10px] text-parchment-ink/60 tracking-widest uppercase mb-1 block">
                    The Message
                  </label>
                  <div className="relative border-b-2 border-parchment-ink/20 focus-within:border-parchment-gold transition-colors">
                    <textarea
                      name="message"
                      value={formState.message}
                      onChange={handleChange}
                      required
                      rows={3}
                      className="w-full bg-transparent py-2 font-cormorant text-base text-parchment-ink placeholder:text-parchment-ink/30 focus:outline-none resize-none"
                      placeholder="Inscribe thy inquiry here..."
                    />
                  </div>
                </div>

                {/* Submit button */}
                <div className="flex justify-center pt-4">
                  <button
                    type="submit"
                    className="relative group px-6 py-3 bg-parchment-crimson rounded-full shadow-lg shadow-parchment-crimson/20 hover:shadow-xl hover:shadow-parchment-crimson/30 transition-all duration-300 hover:scale-105"
                  >
                    <span className="flex items-center gap-2">
                      <span className="font-cinzel text-xs text-white tracking-widest uppercase">
                        {isSubmitted ? "Sent by Raven" : "Seal & Send"}
                      </span>
                    </span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
