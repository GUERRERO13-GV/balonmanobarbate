/* Club Balonmano Barbate — comportamiento de la interfaz
   Desarrollo: Fran Vidal (FranVi) */
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    // Mantiene aria-expanded y aria-label acordes al estado real del menú
    var sincronizar = function (isOpen) {
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      toggle.setAttribute('aria-label', isOpen ? 'Cerrar menú' : 'Abrir menú');
    };

    toggle.addEventListener('click', function () {
      sincronizar(nav.classList.toggle('open'));
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('open');
        sincronizar(false);
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        sincronizar(false);
        toggle.focus();
      }
    });
  }

  // Botón de tema claro / oscuro. theme.js ya aplicó el guardado antes de
  // pintar; aquí solo se gestiona el cambio manual.
  var botonTema = document.querySelector('.theme-toggle');
  if (botonTema) {
    var temaActual = function () {
      var puesto = document.documentElement.getAttribute('data-theme');
      if (puesto) return puesto;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };
    var etiquetar = function () {
      var oscuro = temaActual() === 'dark';
      botonTema.setAttribute('aria-label', oscuro ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro');
      botonTema.setAttribute('aria-pressed', oscuro ? 'true' : 'false');
    };
    etiquetar();
    botonTema.addEventListener('click', function () {
      var nuevo = temaActual() === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nuevo);
      try { localStorage.setItem('tema', nuevo); } catch (e) {}
      etiquetar();
    });
  }

  // El header se estrecha en cuanto la página se separa del principio. Se
  // apunta con una clase en el body porque de --header-h dependen también el
  // menú móvil y el scroll-margin de los anclajes.
  var marcarScroll = function () {
    document.body.classList.toggle('is-scrolled', window.scrollY > 24);
  };
  marcarScroll();
  window.addEventListener('scroll', marcarScroll, { passive: true });

  // Aparición al desplazar. El atributo lo pone el script, nunca el HTML: si
  // el JS no llega a ejecutarse, el contenido se ve igual desde el principio.
  var quietud = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !quietud.matches) {
    var observador = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        entrada.target.classList.add('is-visible');
        obs.unobserve(entrada.target);
      });
    }, { rootMargin: '0px 0px -12% 0px' });

    // El mosaico de la galería va en columnas CSS: transformar sus hijos
    // rompe el reparto, así que ahí se anima el bloque entero, no cada foto.
    var selector = '.section-head, .disciplines, .grid > *, .foto-ancha,' +
                   ' .foto-destacada, .galeria, .lista-contacto, .map-embed';
    document.querySelectorAll(selector).forEach(function (el) {
      if (el.closest('.galeria')) return;
      el.setAttribute('data-reveal', '');
      observador.observe(el);
    });

    // Escalonado corto dentro de cada rejilla: los hermanos entran seguidos,
    // no todos de golpe. Se corta a los 4 para no hacer esperar al visitante.
    document.querySelectorAll('.grid').forEach(function (rejilla) {
      Array.prototype.forEach.call(rejilla.children, function (hijo, i) {
        hijo.style.setProperty('--reveal-delay', Math.min(i, 3) * 90 + 'ms');
      });
    });
  }

  // Season tabs (preparado para futuras temporadas; hoy solo hay una)
  document.querySelectorAll('.season-tabs').forEach(function (tabs) {
    var buttons = tabs.querySelectorAll('button');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        buttons.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var target = btn.getAttribute('data-target');
        var panelGroup = tabs.parentElement.querySelectorAll('.season-panel');
        panelGroup.forEach(function (p) {
          p.style.display = (p.dataset.season === target) ? '' : 'none';
        });
      });
    });
  });
});

