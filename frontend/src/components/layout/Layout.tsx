import { Outlet } from 'react-router-dom';
import Footer from './Footer';
import Header from './Header';
import SideNav from './SideNav';

export default function Layout() {
  return (
    <>
      <a href="#main" className="skip">
        Skip to main content
      </a>
      <Header />
      <div className="block lg:grid lg:min-h-[900px] lg:grid-cols-[256px_minmax(0,1fr)]">
        <SideNav />
        <main id="main" className="px-4 pb-12 pt-8 sm:px-8">
          <Outlet />
          <Footer />
        </main>
      </div>
    </>
  );
}
