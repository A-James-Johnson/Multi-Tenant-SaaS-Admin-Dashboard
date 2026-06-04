import './globals.css';
import { Providers } from '@/components/Providers';

export const metadata = {
  title: 'SaaS Admin Dashboard',
  description: 'Multi-Tenant SaaS Admin Dashboard',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
