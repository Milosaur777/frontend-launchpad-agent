"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Calendar, MapPin, Navigation } from "lucide-react";

const conventions = [
  {
    id: 'queercon',
    name: 'QueerCon',
    date: 'July 30–31',
    venue: 'Mäster Olofsgården',
    address: 'Svartmangatan 6, Gamla Stan, Stockholm',
    coords: { lat: 59.3233, lng: 18.0717 },
    color: '#c2ac7b',
    status: 'upcoming' as const,
    travelGuide: 'Metro to Gamla Stan (red line). Walk toward Österlånggatan, then turn onto Svartmangatan. Mäster Olofsgården is right in the heart of Gamla Stan, just a few minutes from the metro.',
    note: 'Artist Alley booth',
  },
  {
    id: 'narcon',
    name: 'Närcon Sommar',
    date: 'July 23–26',
    venue: 'Linköping University',
    address: 'Campus Valla, Linköping',
    coords: { lat: 58.3962, lng: 15.5750 },
    color: '#1e6b8a',
    status: 'upcoming' as const,
    travelGuide: 'Train to Linköping C (about 2 hours from Stockholm). Take bus 13 or 22 to "Universitetet". The event is held at Campus Valla — follow the signs from the main entrance.',
    note: 'Attending, but not selling at the artist alley',
  },
  {
    id: 'seriefestivalen',
    name: 'Seriefestivalen',
    date: 'May 15–17, 2026',
    venue: 'Kulturhuset',
    address: 'Sergels Torg 3, Stockholm',
    coords: { lat: 59.3325, lng: 18.0645 },
    color: '#8b0000',
    status: 'ended' as const,
    travelGuide: 'Metro to T-Centralen or Hötorget (blue/red/green line). Kulturhuset is located at Sergels Torg with an entrance at street level. Easily accessible from anywhere in Stockholm.',
  },
];

const springSoft = { type: "spring" as const, stiffness: 200, damping: 20 };

export default function ConScheduleSection() {
  const [expandedCon, setExpandedCon] = useState<string | null>(null);

  return (
    <section id="events" className="relative py-24 md:py-32 px-6 overflow-hidden">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={springSoft}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 rounded-full bg-[#1a1a2e] px-4 py-2 border border-[#c2ac7b]/30 mb-6">
            <Calendar className="w-4 h-4 text-[#c2ac7b]" />
            <span className="text-sm font-semibold text-storm-moon">Catch Me At</span>
          </div>
          <h2 className="font-exocet text-4xl md:text-5xl text-parchment-gold mb-4 subtitle-pulse">
            Con Schedule
          </h2>
          <div className="relative w-48 md:w-64 h-6 mx-auto mb-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
          <p className="font-cormorant text-lg text-storm-moon/70 max-w-xl mx-auto">
            Find me at conventions across Sweden. I will be selling prints, stickers, and original art.
          </p>
        </motion.div>

        {/* Convention Cards */}
        <div className="space-y-6">
          {conventions.map((con, i) => {
            const isExpanded = expandedCon === con.id;
            return (
              <motion.div
                key={con.id}
                initial={{ opacity: 0, x: i % 2 === 0 ? -40 : 40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ ...springSoft, delay: i * 0.15 }}
                layout
              >
                <motion.div
                  className="relative bg-[#1a1a2e] border border-[#262626] rounded-lg p-6 md:p-8 overflow-hidden cursor-pointer transition-all duration-200 hover:border-[#404040]"
                  whileHover={{ scale: 1.01, transition: springSoft }}
                  onClick={() => setExpandedCon(isExpanded ? null : con.id)}
                  layout
                >
                  {/* Energy line accent */}
                  <div 
                    className="absolute left-0 top-0 bottom-0 w-1 rounded-full" 
                    style={{ 
                      backgroundColor: con.color, 
                      boxShadow: `0 0 15px ${con.color}` 
                    }} 
                  />

                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pl-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center bg-[#0a0a0f] border border-[#262626]"
                        >
                          <MapPin className="w-5 h-5" style={{ color: con.color, filter: `drop-shadow(0 0 5px ${con.color})` }} />
                        </div>
                        <h3 className="font-exocet text-xl text-storm-moon">
                          {con.name}
                        </h3>
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-storm-moon/60">
                        <span className="flex items-center gap-1.5 text-sm font-cormorant">
                          <Calendar className="w-4 h-4" style={{ color: con.color }} />
                          {con.date}
                        </span>
                        <span className="flex items-center gap-1.5 text-sm font-cormorant">
                          <MapPin className="w-4 h-4" style={{ color: con.color }} />
                          {con.venue}
                        </span>
                        {con.note && (
                          <span className="flex items-center gap-1.5 text-sm text-[#c2ac7b] italic font-cormorant">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#c2ac7b]" />
                            {con.note}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <span 
                        className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border font-cormorant" 
                        style={{ 
                          borderColor: con.status === 'ended' ? '#262626' : `${con.color}40`, 
                          color: con.status === 'ended' ? '#737373' : con.color 
                        }}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${con.status === 'ended' ? 'bg-[#737373]' : 'bg-[#c2ac7b]'}`} />
                        {con.status === 'ended' ? 'Ended' : 'Upcoming'}
                      </span>
                      <motion.div
                        animate={{ rotate: isExpanded ? 180 : 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <img
                          src="/images/arrow-down.avif"
                          alt="Expand"
                          className="w-5 h-5 md:w-6 md:h-6 object-contain"
                        />
                      </motion.div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.4, ease: 'easeOut' }}
                        className="overflow-hidden"
                      >
                        <div className="pt-6 pl-4">
                          <div className="h-px bg-gradient-to-r from-transparent via-[#c2ac7b]/30 to-transparent mb-6" />

                          <div className="grid md:grid-cols-2 gap-6">
                            {/* Map */}
                            <div className="rounded-lg overflow-hidden border border-[#262626] h-[220px] md:h-[260px]">
                              <iframe
                                src={`https://maps.google.com/maps?q=${con.coords.lat},${con.coords.lng}&z=15&output=embed`}
                                width="100%"
                                height="100%"
                                style={{ border: 0 }}
                                allowFullScreen
                                loading="lazy"
                                referrerPolicy="no-referrer-when-downgrade"
                                title={`Map of ${con.name}`}
                              />
                            </div>

                            {/* Travel guide */}
                            <div className="flex flex-col justify-center">
                              <h4 className="font-cinzel text-sm font-semibold text-[#c2ac7b] mb-3 flex items-center gap-2">
                                <Navigation className="w-4 h-4" />
                                How to Get There
                              </h4>
                              <p className="font-cormorant text-sm text-storm-moon/70 leading-relaxed mb-3">
                                {con.travelGuide}
                              </p>
                              <p className="font-cormorant text-xs text-storm-moon/50">
                                <span className="text-[#c2ac7b]">📍</span> {con.address}
                              </p>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
