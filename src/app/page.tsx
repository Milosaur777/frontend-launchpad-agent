"use client";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowRight, Code, Globe, Mail, Zap, Users, Clock, Award } from "lucide-react";
import { motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1] as const,
    },
  }),
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1] as const,
    },
  },
};

const stats = [
  { icon: Zap, label: "Projects", value: "50+" },
  { icon: Users, label: "Clients", value: "30+" },
  { icon: Clock, label: "Years", value: "5+" },
  { icon: Award, label: "Awards", value: "12" },
];

const skills = [
  "React", "Next.js", "TypeScript", "Tailwind CSS", "Node.js",
  "PostgreSQL", "Supabase", "Framer Motion", "Figma", "Git",
];

export default function Home() {
  return (
    <div className="flex flex-col flex-1">
      {/* Navigation */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md"
      >
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <span className="font-mono text-sm font-medium tracking-tight text-primary">
            frontend-designer
          </span>
          <nav className="hidden items-center gap-6 text-sm font-medium text-secondary-foreground md:flex">
            <a href="#work" className="transition-colors hover:text-foreground">
              Work
            </a>
            <a href="#about" className="transition-colors hover:text-foreground">
              About
            </a>
            <a href="#contact" className="transition-colors hover:text-foreground">
              Contact
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label="Code"
            >
              <Code className="h-4 w-4" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label="Globe"
            >
              <Globe className="h-4 w-4" />
            </a>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <main className="flex flex-1 flex-col">
        <section className="relative flex flex-col items-center justify-center px-6 py-32 md:py-40">
          <div className="mx-auto max-w-3xl text-center">
            <motion.div
              custom={0}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
            >
              <Badge
                variant="secondary"
                className="mb-6 font-mono text-xs font-medium tracking-wide text-muted-foreground"
              >
                Available for freelance work
              </Badge>
            </motion.div>
            
            <motion.h1
              custom={1}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl"
            >
              Building digital
              <br />
              <span className="text-primary">experiences</span> that matter.
            </motion.h1>
            
            <motion.p
              custom={2}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground md:text-lg"
            >
              Frontend engineer and designer specializing in React, Next.js, and 
              accessible UI. I craft performant, beautiful web applications for 
              startups and enterprises.
            </motion.p>
            
            <motion.div
              custom={3}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
            >
              <a
                href="#work"
                className="inline-flex h-9 items-center justify-center gap-1.5 rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                View my work
                <ArrowRight className="h-4 w-4" />
              </a>
              <a
                href="mailto:hello@example.com"
                className="inline-flex h-9 items-center justify-center gap-1.5 rounded-md border border-border bg-background px-6 text-sm font-medium text-foreground transition-colors hover:bg-muted"
              >
                <Mail className="h-4 w-4" />
                Get in touch
              </a>
            </motion.div>
          </div>

          {/* Animated gradient glow */}
          <motion.div
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
            aria-hidden="true"
          >
            <div className="absolute left-1/2 top-0 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-3xl" />
          </motion.div>
        </section>

        {/* Stats Section */}
        <section className="px-6 py-16">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="mx-auto grid max-w-5xl grid-cols-2 gap-8 md:grid-cols-4"
          >
            {stats.map((stat) => (
              <motion.div
                key={stat.label}
                variants={staggerItem}
                className="flex flex-col items-center text-center"
              >
                <stat.icon className="mb-3 h-5 w-5 text-primary" />
                <div className="text-3xl font-bold tracking-tight text-foreground">
                  {stat.value}
                </div>
                <div className="mt-1 text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </section>

        <Separator className="mx-auto max-w-5xl" />

        {/* Skills Section */}
        <section className="px-6 py-24 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-5xl text-center"
          >
            <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
              Tech Stack
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              Technologies I use to build modern, scalable applications.
            </p>
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="mt-10 flex flex-wrap justify-center gap-3"
            >
              {skills.map((skill) => (
                <motion.div key={skill} variants={staggerItem}>
                  <Badge
                    variant="secondary"
                    className="px-4 py-2 text-sm font-medium transition-colors hover:bg-primary/10 hover:text-primary"
                  >
                    {skill}
                  </Badge>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </section>

        <Separator className="mx-auto max-w-5xl" />

        {/* Selected Work Preview */}
        <section id="work" className="px-6 py-24 md:py-32">
          <div className="mx-auto max-w-5xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="mb-12 flex items-end justify-between"
            >
              <div>
                <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
                  Selected Work
                </h2>
                <p className="mt-2 text-muted-foreground">
                  A few projects I am proud of.
                </p>
              </div>
              <a
                href="#"
                className="hidden items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground md:inline-flex"
              >
                View all
                <ArrowRight className="h-4 w-4" />
              </a>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid gap-6 md:grid-cols-2"
            >
              {[1, 2, 3, 4].map((i) => (
                <motion.div
                  key={i}
                  variants={staggerItem}
                  whileHover={{ y: -4 }}
                  transition={{ duration: 0.2 }}
                  className="group relative overflow-hidden rounded-lg border border-border bg-card p-6 transition-colors hover:border-border-hover"
                >
                  <div className="aspect-video w-full rounded-md bg-muted transition-colors group-hover:bg-muted/80" />
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold text-card-foreground">
                      Project {i}
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      A brief description of the project and the technologies used.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <Badge variant="secondary" className="text-xs">
                      React
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      Next.js
                    </Badge>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        <Separator className="mx-auto max-w-5xl" />

        {/* CTA Section */}
        <section id="contact" className="px-6 py-24 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-3xl text-center"
          >
            <h2 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
              Let&apos;s work together
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              Have a project in mind? I&apos;d love to hear about it. Let&apos;s discuss how we can bring your ideas to life.
            </p>
            <div className="mt-10">
              <a
                href="mailto:hello@example.com"
                className="inline-flex h-9 items-center justify-center gap-1.5 rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                <Mail className="h-4 w-4" />
                Get in touch
              </a>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border px-6 py-12">
          <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-sm text-muted-foreground">
              © 2026 Frontend Designer. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                aria-label="Code"
              >
                <Code className="h-4 w-4" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                aria-label="Globe"
              >
                <Globe className="h-4 w-4" />
              </a>
              <a
                href="mailto:hello@example.com"
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                aria-label="Email"
              >
                <Mail className="h-4 w-4" />
              </a>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
