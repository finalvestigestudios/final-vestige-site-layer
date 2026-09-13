(() => {
  const stagesRoot = document.querySelector('[data-fv-invest-stages]');
  const img = document.querySelector('[data-fv-invest-image]');
  const captionEl = document.querySelector('[data-fv-invest-caption]');
  const provenanceEl = document.querySelector('[data-fv-invest-provenance]');
  if (!stagesRoot || !img || !captionEl || !provenanceEl) return;

  const stages = Array.from(stagesRoot.querySelectorAll('[data-stage]'));
  if (!stages.length) return;

  // Real NASA imagery already published on this Final Vestige investigation
  // ("The Hatch Opened Inward" — Apollo 1), one image per narrative beat.
  const quoteEl = document.querySelector('[data-fv-invest-quote]');

  const EVIDENCE = [
    {
      src: 'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp?resize=1041%2C810&ssl=1',
      alt: 'Apollo 1 astronauts Gus Grissom, Ed White and Roger Chaffee near Launch Complex 34 during training in January 1967.',
      caption: 'Gus Grissom, Ed White and Roger Chaffee near Launch Complex 34, January 1967.',
      credit: 'NASA · S67-19766',
      href: 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
      quote: 'The easiest way to understand the Apollo 1 fire is to look at two hatches.',
    },
    {
      src: 'https://i0.wp.com/images-assets.nasa.gov/image/S67-15717/S67-15717~large.jpg?resize=1514%2C1920&ssl=1',
      alt: 'Apollo Command and Service Module 012 during preflight processing before the Apollo 1 launch-pad fire.',
      caption: 'Apollo Spacecraft 012 during preflight processing, January 1967.',
      credit: 'NASA · S67-15717',
      href: 'https://www.nasa.gov/image-detail/amf-s67-15717/',
      quote: '"Apollo used pure oxygen" often gets offered as the complete cause of the fire. It wasn’t.',
    },
    {
      src: 'https://i0.wp.com/images-assets.nasa.gov/image/S66-58038/S66-58038~large.jpg?resize=1920%2C1546&ssl=1',
      alt: 'The Apollo 1 crew preparing to enter a command module during preflight training in 1966.',
      caption: 'The Apollo 1 crew entering the spacecraft during training, 1966.',
      credit: 'NASA · S66-58038',
      href: 'https://www.nasa.gov/image-detail/amf-s66-58038/',
      quote: 'No single ignition source was conclusively identified.',
    },
    {
      src: 'https://i0.wp.com/images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0164/KSC-20170124-PH_KLS01_0164~large.jpg?resize=1920%2C1280&ssl=1',
      alt: 'Apollo 1 tribute displaying the original three-part Block I hatch associated with the command module fire.',
      caption: 'The Apollo 1 tribute includes the original three-part Block I hatch.',
      credit: 'NASA/Kim Shiflett · KSC-20170124-PH_KLS01_0164',
      href: 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
      quote: 'The inner pressure hatch opened inward.',
    },
    {
      src: 'https://i0.wp.com/images-assets.nasa.gov/image/S67-21294/S67-21294~large.jpg?resize=1920%2C1297&ssl=1',
      alt: 'Interior of Apollo Command Module 012 after the January 27, 1967 fire, showing severe heat and fire damage.',
      caption: 'The interior of Command Module 012 after the fire.',
      credit: 'NASA · S67-21294',
      href: 'https://www.nasa.gov/image-detail/amf-s67-21294/',
      quote: 'Fourteen seconds is more useful than saying the spacecraft "exploded."',
    },
    {
      src: 'https://i0.wp.com/images-assets.nasa.gov/image/KSC-20170124-PH_KLS01_0090/KSC-20170124-PH_KLS01_0090~large.jpg?resize=1280%2C1920&ssl=1',
      alt: 'Redesigned unified Apollo hatch developed after the Apollo 1 fire to open outward within seconds.',
      caption: 'The redesigned Block II hatch, displayed in the Apollo 1 tribute.',
      credit: 'NASA/Kim Shiflett · KSC-20170124-PH_KLS01_0090',
      href: 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
      quote: 'The replacement did not open inward.',
    },
  ];

  const activate = (i) => {
    stages.forEach((s) => s.removeAttribute('data-fv-active'));
    stages[i].setAttribute('data-fv-active', '1');
    const ev = EVIDENCE[i] || EVIDENCE[0];
    img.src = ev.src;
    img.alt = ev.alt;
    captionEl.textContent = ev.caption;
    provenanceEl.textContent = '';
    provenanceEl.append(ev.credit + ' · ');
    const a = document.createElement('a');
    a.href = ev.href;
    a.textContent = 'Source record ↗';
    provenanceEl.append(a);
    if (quoteEl) quoteEl.textContent = '“' + ev.quote + '”';
  };

  stages.forEach((stage, i) => {
    stage.addEventListener('click', () => activate(i));
    stage.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(i); }
    });
  });

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const i = stages.indexOf(entry.target);
          if (i >= 0) activate(i);
        }
      });
    }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });
    stages.forEach((s) => io.observe(s));
  }
})();
