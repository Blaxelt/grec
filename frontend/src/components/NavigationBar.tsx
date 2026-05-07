import { Link, useLocation } from "react-router-dom";
import { useTheme } from "../hooks/useTheme";

const navItems = [
    { label: "Home", to: "/" },
    { label: "Search", to: "/search" },
    { label: "Profile", to: "/profile" },
];

export function NavigationBar() {
    const { pathname } = useLocation();
    const { theme, toggle } = useTheme();

    return (
        <nav className="flex items-center h-14 px-10 bg-surface border-b border-border gap-8">
            <Link to="/" className="font-press text-sm tracking-wider text-text shrink-0 mr-4">
                GREC
            </Link>

            <div className="flex items-center gap-1">
                {navItems.map(({ label, to }) => {
                    const isActive = pathname === to;

                    return (
                        <Link
                            key={label}
                            to={to}
                            className={`relative px-3 py-1.5 text-sm font-medium rounded-md transition-colors
                                ${isActive
                                    ? "text-accent"
                                    : "text-text-dim hover:text-text hover:bg-white/5"
                                }`}
                        >
                            {label}
                            {isActive && (
                                <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-accent rounded-full" />
                            )}
                        </Link>
                    );
                })}
            </div>

            <a
                href="https://github.com/Blaxelt/grec"
                target="_blank"
                rel="noopener noreferrer"
                title="GitHub"
                className="ml-auto cursor-pointer"
            >
                <img src="/github_logo.svg" alt="GitHub" className="w-6 h-6" />
            </a>

            <button
                onClick={toggle}
                title="Toggle theme"
                className="text-lg text-text-dim hover:text-text transition-colors cursor-pointer"
            >
                {theme === "dark" ? "🌙" : "☀️"}
            </button>
        </nav>
    );
}