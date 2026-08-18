/* Club Balonmano Barbate — comportamiento de la interfaz
   Desarrollo: Francisco Vidal Mateo (FranVi) */
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
    // Cerrar el menú deja también recogidos los submenús: si no, al volver a
    // abrirlo aparecería desplegado por donde se quedó.
    var recoger = function () {
      nav.querySelectorAll('.nav-grupo').forEach(function (g) {
        g.classList.remove('abierto');
        var b = g.querySelector('.nav-mas'), pa = g.querySelector('.nav-sub');
        if (b) b.setAttribute('aria-expanded', 'false');
        if (pa) pa.hidden = true;
      });
    };
    toggle.addEventListener('click', function () {
      if (!nav.classList.contains('open')) recoger();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        sincronizar(false);
        toggle.focus();
      }
    });
  }


  // ---------- Submenús de la navegación ----------
  // Patrón de disclosure: un botón por grupo que abre y cierra su panel. El
  // panel se oculta con el atributo hidden, así que estando cerrado no es
  // alcanzable con el tabulador. Cierra con Escape, al pulsar fuera y al
  // salir el foco del grupo.
  var grupos = Array.prototype.slice.call(document.querySelectorAll('.nav-grupo'));
  if (grupos.length) {
    var cerrarGrupos = function (salvo) {
      grupos.forEach(function (g) {
        if (g === salvo) return;
        g.classList.remove('abierto');
        var b = g.querySelector('.nav-mas');
        var panel = g.querySelector('.nav-sub');
        if (b) b.setAttribute('aria-expanded', 'false');
        if (panel) panel.hidden = true;
      });
    };

    grupos.forEach(function (grupo) {
      var boton = grupo.querySelector('.nav-mas');
      var panel = grupo.querySelector('.nav-sub');
      if (!boton || !panel) return;
      var etiqueta = grupo.querySelector('a') ? grupo.querySelector('a').textContent.trim() : '';

      var poner = function (abierto) {
        grupo.classList.toggle('abierto', abierto);
        boton.setAttribute('aria-expanded', abierto ? 'true' : 'false');
        boton.setAttribute('aria-label', (abierto ? 'Cerrar' : 'Abrir') + ' el submenú de ' + etiqueta);
        panel.hidden = !abierto;
      };

      boton.addEventListener('click', function (e) {
        e.stopPropagation();
        var abrir = panel.hidden;
        cerrarGrupos(grupo);
        poner(abrir);
      });

      // Con ratón el submenú se abre al pasar por encima: obligar a acertar en
      // el chevrón es incómodo. La guarda (hover:hover) y (pointer:fine) deja
      // fuera a los táctiles, donde el hover no existe y provoca aperturas
      // fantasma al desplazar.
      var conRaton = window.matchMedia('(hover: hover) and (pointer: fine)');
      grupo.addEventListener('mouseenter', function () {
        if (!conRaton.matches) return;
        cerrarGrupos(grupo);
        poner(true);
      });
      grupo.addEventListener('mouseleave', function () {
        if (!conRaton.matches) return;
        poner(false);
      });

      // Al elegir una opción, el submenú y el menú móvil se cierran.
      panel.querySelectorAll('a').forEach(function (enlace) {
        enlace.addEventListener('click', function () { poner(false); });
      });

      grupo.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape' || panel.hidden) return;
        poner(false);
        boton.focus();
      });

      // Si el foco se va del grupo con el tabulador, se cierra solo.
      grupo.addEventListener('focusout', function (e) {
        if (panel.hidden) return;
        if (!grupo.contains(e.relatedTarget)) poner(false);
      });
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.nav-grupo')) cerrarGrupos(null);
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

  // Movimiento. Uno solo y con intención: el titular de cada banda de foto se
  // descubre tras una máscara, como una copia que sale del revelador, y la
  // foto de fondo cierra un acercamiento muy lento. Nada más se anima al
  // desplazar: el fundido idéntico repetido en cada bloque es precisamente lo
  // que delata una plantilla.
  // Los atributos los pone el script, nunca el HTML: si el JS no llega a
  // ejecutarse, todo se ve desde el primer momento.
  var quietud = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !quietud.matches) {
    var observador = new IntersectionObserver(function (entradas, obs) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        entrada.target.classList.add('visible');
        obs.unobserve(entrada.target);
      });
    }, { rootMargin: '0px 0px -14% 0px' });

    document.querySelectorAll('.banda-foto').forEach(function (banda) {
      // El rótulo, el titular y la entradilla se descubren escalonados: es el
      // orden en que se leen, no un efecto repartido por igual.
      var piezas = banda.querySelectorAll(
        '.container > .eyebrow, .container > h1, .container > h2,' +
        ' .container > .lead, .container > .banda-datos, .container > .hero-actions'
      );
      piezas.forEach(function (pieza, i) {
        pieza.setAttribute('data-mascara', '');
        pieza.style.setProperty('--mascara-delay', 90 + i * 110 + 'ms');
      });

      if (banda.querySelector('.banda-media img')) {
        banda.setAttribute('data-entra', '');
      }

      // La banda de portada está visible al cargar: si se esperase al
      // observador, el titular aparecería tarde y en blanco.
      var arranque = banda.getBoundingClientRect().top < window.innerHeight * 0.9;
      if (arranque) {
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            banda.classList.add('visible');
            piezas.forEach(function (pieza) { pieza.classList.add('visible'); });
          });
        });
      } else {
        observador.observe(banda);
        piezas.forEach(function (pieza) { observador.observe(pieza); });
      }
    });
  }


  // ---------- Visor de fotos ----------
  // El diálogo lo construye el script, no el HTML: sin JS las fotos siguen
  // siendo enlaces normales a la imagen y no queda un modal muerto en la
  // página. Lleva las cuatro cosas que exige un modal accesible: Escape,
  // trampa de foco, bloqueo del scroll y devolución del foco al cerrar.
  var figuras = Array.prototype.slice.call(document.querySelectorAll('.galeria .card[data-visor]'));
  if (figuras.length) {
    var visor = document.createElement('div');
    visor.className = 'visor';
    visor.setAttribute('role', 'dialog');
    visor.setAttribute('aria-modal', 'true');
    visor.setAttribute('aria-label', 'Visor de fotografías');
    visor.hidden = true;
    visor.innerHTML =
      '<button class="visor-cerrar" type="button" aria-label="Cerrar el visor">&times;</button>' +
      '<button class="visor-nav visor-antes" type="button" aria-label="Foto anterior">&#8249;</button>' +
      '<button class="visor-nav visor-luego" type="button" aria-label="Foto siguiente">&#8250;</button>' +
      '<figure class="visor-marco">' +
      '  <picture><source class="visor-webp" type="image/webp"><img class="visor-img" alt=""></picture>' +
      '  <figcaption class="visor-pie"></figcaption>' +
      '</figure>';
    document.body.appendChild(visor);

    var vImg = visor.querySelector('.visor-img');
    var vWebp = visor.querySelector('.visor-webp');
    var vPie = visor.querySelector('.visor-pie');
    var bCerrar = visor.querySelector('.visor-cerrar');
    var bAntes = visor.querySelector('.visor-antes');
    var bLuego = visor.querySelector('.visor-luego');
    var indice = 0;
    var devolverFoco = null;

    var pintar = function (i) {
      indice = (i + figuras.length) % figuras.length;
      var fig = figuras[indice];
      var pie = fig.querySelector('figcaption');
      var texto = pie ? pie.textContent.trim() : '';
      vWebp.srcset = fig.getAttribute('data-visor');
      vImg.src = fig.getAttribute('data-visor-jpg') || fig.getAttribute('data-visor');
      vImg.alt = texto;
      vPie.textContent = texto;
      visor.setAttribute('aria-label', 'Foto ' + (indice + 1) + ' de ' + figuras.length);
    };

    var abrir = function (i, origen) {
      devolverFoco = origen || null;
      pintar(i);
      visor.hidden = false;
      document.body.classList.add('sin-scroll');
      bCerrar.focus();
    };

    var cerrar = function () {
      visor.hidden = true;
      document.body.classList.remove('sin-scroll');
      if (devolverFoco && devolverFoco.focus) devolverFoco.focus();
      devolverFoco = null;
    };

    figuras.forEach(function (fig, i) {
      // La foto pasa a ser un control de verdad: alcanzable con el tabulador
      // y activable con Intro o espacio, no solo con el ratón.
      var img = fig.querySelector('img');
      fig.setAttribute('tabindex', '0');
      fig.setAttribute('role', 'button');
      fig.setAttribute('aria-label', 'Ampliar: ' + (img ? img.alt : 'fotografía'));
      fig.addEventListener('click', function () { abrir(i, fig); });
      fig.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); abrir(i, fig); }
      });
    });

    bCerrar.addEventListener('click', cerrar);
    bAntes.addEventListener('click', function () { pintar(indice - 1); });
    bLuego.addEventListener('click', function () { pintar(indice + 1); });
    // Pulsar el fondo cierra; pulsar la foto, no.
    visor.addEventListener('click', function (e) { if (e.target === visor) cerrar(); });

    document.addEventListener('keydown', function (e) {
      if (visor.hidden) return;
      if (e.key === 'Escape') { cerrar(); return; }
      if (e.key === 'ArrowLeft') { pintar(indice - 1); return; }
      if (e.key === 'ArrowRight') { pintar(indice + 1); return; }
      if (e.key !== 'Tab') return;
      // Trampa de foco: el tabulador no puede salirse del diálogo.
      var focos = visor.querySelectorAll('button');
      var primero = focos[0], ultimo = focos[focos.length - 1];
      if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
    });
  }


  // ---------- Marcos de terceros, solo bajo demanda ----------
  // El iframe de Google enviaba la IP del visitante a seis dominios suyos nada
  // más entrar en contacto.html, sin que nadie lo pidiera; el de la federación
  // contacta con Google Analytics. Ninguno se inserta hasta que se pulsa.
  // Sin JS queda siempre un enlace normal al sitio de origen, que tampoco
  // carga nada por su cuenta.
  document.querySelectorAll('.marco-diferido').forEach(function (hueco) {
    var boton = hueco.querySelector('button');
    if (!boton) return;
    boton.addEventListener('click', function () {
      var marco = document.createElement('iframe');
      marco.className = 'marco-cargado';
      marco.title = hueco.getAttribute('data-titulo') || 'Contenido externo';
      marco.loading = 'lazy';
      marco.referrerPolicy = 'no-referrer';
      marco.setAttribute('allowfullscreen', '');
      marco.style.height = (hueco.getAttribute('data-alto') || '460') + 'px';
      marco.src = hueco.getAttribute('data-src');
      hueco.replaceWith(marco);
    });
  });


  // ---------- Sumario de competiciones de la federación ----------
  // Un solo marco para todas: al elegir una competición se carga ahí. Así el
  // visitante decide qué mira y solo se hace una llamada a la federación, no
  // una por equipo. El aviso de privacidad va encima del sumario, para que se
  // lea antes del primer clic.
  var huecoTabla = document.getElementById('tabla-federacion');
  if (huecoTabla) {
    var botones = Array.prototype.slice.call(document.querySelectorAll('.comp-ver'));
    var marcoActual = null;

    var cargar = function (boton) {
      botones.forEach(function (b) {
        var fila = b.closest('li');
        var activo = b === boton;
        if (fila) fila.classList.toggle('activa', activo);
        b.setAttribute('aria-pressed', activo ? 'true' : 'false');
      });

      if (!marcoActual) {
        marcoActual = document.createElement('iframe');
        marcoActual.className = 'marco-cargado';
        marcoActual.loading = 'lazy';
        marcoActual.referrerPolicy = 'no-referrer';
        marcoActual.setAttribute('allowfullscreen', '');
        marcoActual.style.height = '820px';
        huecoTabla.innerHTML = '';
        huecoTabla.appendChild(marcoActual);
      }
      marcoActual.title = 'Clasificación y calendario: ' + boton.getAttribute('data-nombre');
      marcoActual.src = boton.getAttribute('data-src');
      // El foco va a la tabla recién cargada: si no, quien navega con teclado
      // pulsa y no sabe que ha pasado nada más abajo.
      huecoTabla.setAttribute('tabindex', '-1');
      huecoTabla.focus({ preventScroll: true });
      huecoTabla.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    botones.forEach(function (boton) {
      boton.setAttribute('aria-pressed', 'false');
      boton.setAttribute('aria-controls', 'tabla-federacion');
      boton.addEventListener('click', function () { cargar(boton); });
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

