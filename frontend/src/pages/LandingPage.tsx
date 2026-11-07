import { Link } from 'react-router-dom';
import {
  Zap,
  Shield,
  Code2,
  Terminal,
  ArrowRight,
  CheckCircle,
  Lock,
  Clock,
  Box,
  Github,
} from 'lucide-react';

const features = [
  {
    icon: Code2,
    title: 'AI Code Generation',
    description:
      'Describe your programming task in plain English. Our backend calls the AI model and returns production-quality Python code.',
  },
  {
    icon: Shield,
    title: 'Sandboxed Execution',
    description:
      'All code runs inside an isolated Docker container. No network access, strict memory limits, and automatic cleanup.',
  },
  {
    icon: Terminal,
    title: 'Full Execution Report',
    description:
      'See stdout, stderr, exit code, duration, timeout status, OOM kill flag, and container cleanup status after every run.',
  },
  {
    icon: Clock,
    title: 'Execution History',
    description:
      'Every generation and execution is persisted. Review your past tasks and results at any time.',
  },
  {
    icon: Lock,
    title: 'Secure Authentication',
    description:
      'JWT-based authentication with rate-limiting, password validation, and per-user data isolation baked in.',
  },
  {
    icon: Box,
    title: 'Zero Blast Radius',
    description:
      'The sandbox enforces strict OS-level isolation. Malicious or buggy code cannot affect the host system.',
  },
];

const steps = [
  {
    num: '01',
    title: 'Describe your task',
    description: 'Write a natural-language prompt: "Write a Python function to merge two sorted lists."',
  },
  {
    num: '02',
    title: 'AI generates code',
    description: 'The backend sends your request to the AI model and returns clean, ready-to-run Python code.',
  },
  {
    num: '03',
    title: 'Review the code',
    description: 'Inspect the generated code with syntax highlighting before you decide to run it.',
  },
  {
    num: '04',
    title: 'Run securely',
    description:
      'Click Run Code. The backend executes it in a Docker sandbox. You see the full output instantly.',
  },
];

const securityHighlights = [
  'Docker container isolation per execution',
  'No internet access inside the sandbox',
  'Memory and CPU limits enforced',
  'Configurable execution timeout (1–30 s)',
  'Automatic container cleanup after every run',
  'Output size capped to prevent flooding',
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-900 text-gray-100">
      {/* Nav */}
      <nav className="border-b border-surface-700 bg-surface-900/80 backdrop-blur sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center">
              <Zap size={14} className="text-white" />
            </div>
            <span className="font-bold text-white text-lg">ProofRun</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-ghost text-sm">Log in</Link>
            <Link to="/register" className="btn-primary text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 pt-24 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-950 border border-brand-800 text-brand-300 text-xs font-medium mb-6">
          <Zap size={12} />
          Vultr Agent Rush Hackathon – Challenge 1: Blast Radius Zero
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-5">
          Execute AI-generated code.{' '}
          <span className="text-brand-400">Safely.</span>{' '}
          Verify everything.
        </h1>
        <p className="max-w-2xl mx-auto text-lg text-gray-400 mb-8">
          ProofRun generates Python code from your natural-language description,
          then executes it inside a Docker sandbox so nothing can go wrong on
          the host system.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/register" className="btn-primary text-base px-6 py-3">
            Get Started Free
            <ArrowRight size={18} />
          </Link>
          <Link to="/login" className="btn-secondary text-base px-6 py-3">
            Log in
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-white text-center mb-2">
          Everything you need to run AI code safely
        </h2>
        <p className="text-center text-gray-400 mb-10">
          Built with security and developer experience in mind.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map(({ icon: Icon, title, description }) => (
            <div key={title} className="card hover:border-brand-700 transition-colors">
              <div className="w-9 h-9 rounded-lg bg-brand-600/20 flex items-center justify-center mb-4">
                <Icon size={18} className="text-brand-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-surface-800 border-y border-surface-700 py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white text-center mb-2">How it works</h2>
          <p className="text-center text-gray-400 mb-10">From prompt to verified output in seconds.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map(({ num, title, description }) => (
              <div key={num} className="relative">
                <div className="text-4xl font-bold text-brand-800 mb-3">{num}</div>
                <h3 className="font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security highlights */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="lg:grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-2xl font-bold text-white mb-3">
              Blast Radius Zero
            </h2>
            <p className="text-gray-400 mb-6 leading-relaxed">
              Every line of AI-generated code is a potential risk. ProofRun's
              Docker sandbox enforces OS-level isolation so that whatever the AI
              generates — however dangerous — cannot affect the host system.
            </p>
            <ul className="space-y-3">
              {securityHighlights.map((item) => (
                <li key={item} className="flex items-center gap-3 text-sm text-gray-300">
                  <CheckCircle size={16} className="text-green-400 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-10 lg:mt-0 card bg-surface-700 font-mono text-xs text-gray-300 leading-relaxed">
            <p className="text-brand-400 mb-2"># Execution report</p>
            <p><span className="text-gray-500">status:</span>       <span className="text-green-400">success</span></p>
            <p><span className="text-gray-500">exit_code:</span>    <span className="text-blue-400">0</span></p>
            <p><span className="text-gray-500">duration_ms:</span>  <span className="text-blue-400">143</span></p>
            <p><span className="text-gray-500">timed_out:</span>    <span className="text-purple-400">false</span></p>
            <p><span className="text-gray-500">oom_killed:</span>   <span className="text-purple-400">false</span></p>
            <p><span className="text-gray-500">output_limited:</span><span className="text-purple-400">false</span></p>
            <p><span className="text-gray-500">cleanup_ok:</span>   <span className="text-green-400">true</span></p>
            <div className="mt-3 pt-3 border-t border-surface-600">
              <p className="text-gray-500 mb-1"># stdout</p>
              <p>120</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-950 border-t border-brand-900 py-16 text-center">
        <h2 className="text-2xl font-bold text-white mb-3">Ready to run code safely?</h2>
        <p className="text-brand-300 mb-6">
          Create a free account and start generating and executing code in seconds.
        </p>
        <Link to="/register" className="btn-primary text-base px-6 py-3">
          Create Free Account
          <ArrowRight size={18} />
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-surface-700 py-6 text-center text-gray-500 text-sm">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Zap size={14} className="text-brand-500" />
            <span className="text-gray-400 font-medium">ProofRun</span>
            <span className="text-gray-600">– Vultr Agent Rush Hackathon 2024</span>
          </div>
          <a
            href="https://github.com/Adarsh-5592/ProofRun"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-gray-500 hover:text-gray-300 transition-colors"
          >
            <Github size={14} />
            GitHub
          </a>
        </div>
      </footer>
    </div>
  );
}
