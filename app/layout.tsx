
import "./globals.css";

export const metadata = {
  title: "FORM — Training Adaptation Simulator",
  description:
    "Exercise-driven 3D body adaptation simulator modeling localized muscle hypertrophy across training timelines.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                function shouldIgnore(err) {
                  if (!err) return false;
                  var str = (err.message || err.stack || err.reason || String(err)).toLowerCase();
                  return (
                    str.indexOf('metamask') !== -1 ||
                    str.indexOf('failed to connect to metamask') !== -1 ||
                    str.indexOf('chrome-extension://') !== -1
                  );
                }
                window.addEventListener('error', function(e) {
                  if (shouldIgnore(e.error) || shouldIgnore(e.message)) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return true;
                  }
                }, true);
                window.addEventListener('unhandledrejection', function(e) {
                  if (shouldIgnore(e.reason)) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return true;
                  }
                }, true);
              })();
            `,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
