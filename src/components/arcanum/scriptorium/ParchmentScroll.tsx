"use client";

import { motion, useInView } from "framer-motion";
import { useRef, ReactNode } from "react";

interface ParchmentScrollProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "contract" | "dark";
  hasDropCap?: boolean;
  dropCapLetter?: string;
}

export default function ParchmentScroll({
  children,
  className = "",
  variant = "default",
  hasDropCap = false,
  dropCapLetter = "",
}: ParchmentScrollProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 60, scaleY: 0.8 }}
      animate={isInView ? { opacity: 1, y: 0, scaleY: 1 } : {}}
      transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
      className={`relative ${className}`}
    >
      {/* Three-Part Parchment Scroll */}
      <div className="relative mx-auto max-w-4xl">
        {/* Top rolled edge */}
        <div 
          className="w-full bg-cover bg-center bg-no-repeat"
          style={{ 
            backgroundImage: "url('/images/parchment-top.avif')",
            height: '120px',
          }}
          aria-hidden="true"
        />
        
        {/* Middle body - with content */}
        <div className="relative">
          {/* Middle background image */}
          <div className="absolute inset-0 w-full overflow-hidden">
            <img
              src="/images/parchment-middle.avif"
              alt=""
              className="w-full h-full object-cover object-top"
              aria-hidden="true"
            />
          </div>
          
          {/* Content overlay */}
          <div className="relative px-12 md:px-20 py-8 md:py-12">
            {/* Text content */}
            <div className="relative z-10">
              {hasDropCap && dropCapLetter && (
                <div className="flex items-start gap-2 mb-6">
                  <span className="font-blackletter text-6xl md:text-8xl text-parchment-ink leading-none float-left mr-2">
                    {dropCapLetter}
                  </span>
                  <div className="flex-1">
                    {children}
                  </div>
                </div>
              )}
              {!hasDropCap && children}
            </div>
            
            {/* Wax seal decoration for contract variant */}
            {variant === "contract" && (
              <div className="absolute bottom-12 right-8 md:bottom-16 md:right-12">
                <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-parchment-crimson shadow-lg flex items-center justify-center wax-pulse">
                  <span className="font-blackletter text-xl md:text-2xl text-white">M</span>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Bottom rolled edge with seal */}
        <div 
          className="w-full bg-cover bg-center bg-no-repeat"
          style={{ 
            backgroundImage: "url('/images/parchment-bottom.avif')",
            height: '120px',
          }}
          aria-hidden="true"
        />
      </div>
    </motion.div>
  );
}
