function Logo({ logoSrc, alt: altText }: LogoProps) {
  return <img src={logoSrc} alt={altText} />;
}

interface LogoProps {
  logoSrc: string;
  alt: string;
}

export default Logo;
