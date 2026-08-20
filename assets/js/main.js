/* Club Balonmano Barbate — comportamiento de la interfaz
   Desarrollo: Francisco Vidal Mateo (FranVi) */

/* ---------- Red de seguridad ----------
   El sitio funciona entero sin JavaScript, salvo por una cosa: este script
   tapa los titulares de las bandas de foto con data-mascara y luego los
   descubre. Si algo revienta a mitad —un navegador viejo, una extensión que
   se mete por medio—, esas piezas se quedarían tapadas y la página se vería
   con agujeros. Este guardián las descubre todas y deja el contenido a la
   vista, que es el estado correcto cuando el adorno no se puede pintar.

   No se registra nada en consola en el camino normal: solo se avisa cuando
   de verdad ha fallado algo. */
function revelarContenido() {
  document.querySelectorAll('[data-mascara]').forEach(function (pieza) {
    pieza.removeAttribute('data-mascara');
    pieza.classList.add('visible');
  });
  document.querySelectorAll('.banda-foto[data-entra]').forEach(function (banda) {
    banda.removeAttribute('data-entra');
    banda.classList.add('visible');
  });
}

window.addEventListener('error', function (e) {
  // Solo interesan los errores de este script; los de un iframe de terceros
  // o una imagen suelta no tienen por qué desmontar las animaciones.
  if (e.filename && e.filename.indexOf('main.js') === -1) return;
  revelarContenido();
});

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


  // ---------- Estado de carga y fallo de los marcos ----------
  // El contenido de estos dos marcos lo sirve un tercero (Google y la
  // federación), así que puede tardar y puede no llegar. Las dos cosas se
  // cuentan: mientras carga hay un aviso, y si no llega se dice y se ofrece
  // el enlace directo, que es lo que el visitante venía a ver.
  var ESPERA_MAXIMA = 15000;

  function avisoCarga(texto) {
    var caja = document.createElement('div');
    caja.className = 'cargando';
    // El aviso se anuncia solo: quien usa lector de pantalla acaba de pulsar
    // un botón y necesita saber que algo está pasando.
    caja.setAttribute('role', 'status');
    caja.setAttribute('aria-live', 'polite');
    var p = document.createElement('p');
    p.textContent = texto;
    caja.appendChild(p);
    return caja;
  }

  function avisoFallo(destino, titulo) {
    var caja = document.createElement('div');
    caja.className = 'marco-fallo';
    var p = document.createElement('p');
    p.textContent = 'No se ha podido cargar «' + titulo + '». Puede que el '
      + 'servidor de origen esté caído o que una extensión del navegador lo '
      + 'esté bloqueando.';
    var q = document.createElement('p');
    var a = document.createElement('a');
    a.href = destino;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = 'Abrirlo directamente en el sitio de origen';
    q.appendChild(a);
    caja.appendChild(p);
    caja.appendChild(q);
    return caja;
  }

  // El marco se mete en el DOM ya, porque fuera de él no empieza a cargar,
  // pero oculto: hasta que dispara load solo se ve el aviso.
  function vigilarCarga(marco, espera, destino, titulo) {
    marco.style.display = 'none';
    espera.appendChild(marco);
    var resuelto = false;

    var reloj = setTimeout(function () {
      if (resuelto) return;
      resuelto = true;
      espera.replaceWith(avisoFallo(destino, titulo));
    }, ESPERA_MAXIMA);

    marco.addEventListener('load', function () {
      if (resuelto) return;
      resuelto = true;
      clearTimeout(reloj);
      marco.style.display = '';
      espera.replaceWith(marco);
    });

    marco.addEventListener('error', function () {
      if (resuelto) return;
      resuelto = true;
      clearTimeout(reloj);
      espera.replaceWith(avisoFallo(destino, titulo));
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
      var destino = hueco.getAttribute('data-src');
      var titulo = hueco.getAttribute('data-titulo') || 'Contenido externo';

      // Mientras el marco no pinte, en su sitio va el aviso de carga: son
      // varios segundos contra un servidor ajeno y sin nada que lo diga
      // parece que el botón no ha funcionado.
      var espera = avisoCarga('Cargando el contenido…');
      hueco.replaceWith(espera);

      var marco = document.createElement('iframe');
      marco.className = 'marco-cargado';
      marco.title = titulo;
      marco.loading = 'lazy';
      marco.referrerPolicy = 'no-referrer';
      marco.setAttribute('allowfullscreen', '');
      marco.style.height = (hueco.getAttribute('data-alto') || '460') + 'px';

      vigilarCarga(marco, espera, destino, titulo);
      marco.src = destino;
    });
  });


  // ---------- Sumario de competiciones de la federación ----------
  // Un solo marco a la vez para las 147: al elegir una competición se carga
  // ahí. Así el visitante decide qué mira y solo se hace una llamada a la
  // federación, no una por equipo. El aviso de privacidad va encima del
  // sumario, para que se lea antes del primer clic.
  var huecoTabla = document.getElementById('tabla-federacion');
  if (huecoTabla) {
    var botones = Array.prototype.slice.call(document.querySelectorAll('.comp-ver'));

    var cargar = function (boton) {
      botones.forEach(function (b) {
        var fila = b.closest('li');
        var activo = b === boton;
        if (fila) fila.classList.toggle('activa', activo);
        b.setAttribute('aria-pressed', activo ? 'true' : 'false');
      });

      var nombre = boton.getAttribute('data-nombre');
      var destino = boton.getAttribute('data-src');

      // Marco nuevo en cada carga y no uno reutilizado: reutilizarlo obligaba
      // a colgarle otro par de listeners por clic, y con 147 botones eso se
      // acumula. En pantalla sigue habiendo uno solo.
      var marco = document.createElement('iframe');
      marco.className = 'marco-cargado';
      marco.loading = 'lazy';
      marco.referrerPolicy = 'no-referrer';
      marco.setAttribute('allowfullscreen', '');
      marco.style.height = '820px';
      marco.title = 'Clasificación y calendario: ' + nombre;

      // Cada clasificación son ~2,4 MB contra el servidor de la federación:
      // hay segundos de espera y conviene que se vean. Al cambiar de torneo
      // se vuelve a poner el aviso, porque si no parece que el clic no ha
      // hecho nada.
      var espera = avisoCarga('Cargando la clasificación…');
      huecoTabla.innerHTML = '';
      huecoTabla.appendChild(espera);

      vigilarCarga(marco, espera, destino, nombre);
      marco.src = destino;
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

  // ---------- Cuenta atrás del próximo partido ----------
  // El bloque lo escribe tools/genera_partidos.py con la fecha, el rival y el
  // pabellón ya puestos: esto es un añadido. Nace con [hidden] para que sin JS
  // no quede un hueco, y si la fecha ya pasó se queda oculto en vez de contar
  // hacia atrás (la recogida es semanal, así que puede haberse quedado vieja).
  // La fecha va sin zona horaria a propósito: se lee como hora local, que es
  // la del pabellón y la de casi todo el que mira esta página.
  document.querySelectorAll('.proximo-cuenta[data-cuenta]').forEach(function (el) {
    var cuando = new Date(el.getAttribute('data-cuenta'));
    if (isNaN(cuando)) return;

    function pinta() {
      var faltan = cuando - new Date();
      if (faltan <= 0) { el.hidden = true; return false; }
      var dias = Math.floor(faltan / 86400000);
      var horas = Math.floor((faltan % 86400000) / 3600000);
      var minutos = Math.floor((faltan % 3600000) / 60000);
      var cifra, unidad;
      if (dias >= 1) {
        cifra = dias; unidad = dias === 1 ? 'día para el partido' : 'días para el partido';
      } else if (horas >= 1) {
        cifra = horas; unidad = horas === 1 ? 'hora para el partido' : 'horas para el partido';
      } else {
        cifra = minutos; unidad = minutos === 1 ? 'minuto para el partido' : 'minutos para el partido';
      }
      el.textContent = '';
      el.appendChild(document.createTextNode(cifra));
      var rot = document.createElement('span');
      rot.textContent = unidad;
      el.appendChild(rot);
      el.hidden = false;
      return true;
    }

    if (pinta()) setInterval(pinta, 60000);
  });

  // ---------- Buscador de la página 404 ----------
  // No hay backend ni índice: se filtra la lista que ya está en el HTML. Por
  // eso el campo lo pone el script y no el marcado — sin JavaScript un campo
  // de búsqueda que no busca es peor que ninguno, y la lista entera sigue
  // estando a la vista.
  var zonaBusca = document.querySelector('[data-buscador]');
  var listaBusca = zonaBusca && zonaBusca.querySelector('[data-buscador-lista]');
  if (listaBusca) {
    var entradas = Array.prototype.slice.call(listaBusca.children).map(function (li) {
      return { li: li, texto: li.textContent.toLowerCase() };
    });

    var campo = document.createElement('input');
    campo.type = 'search';
    campo.id = 'buscador-404';
    campo.className = 'buscador-campo';
    campo.placeholder = 'equipos, equipaciones, contacto…';
    campo.autocomplete = 'off';

    var etiqueta = document.createElement('label');
    etiqueta.className = 'eyebrow';
    etiqueta.htmlFor = campo.id;
    etiqueta.textContent = 'Buscar en la web del club';

    var recuento = document.createElement('p');
    recuento.className = 'buscador-recuento';
    // El resultado se dice en voz alta: sin esto, quien no ve la lista no
    // sabe si al escribir ha quedado algo.
    recuento.setAttribute('role', 'status');
    recuento.setAttribute('aria-live', 'polite');

    var caja = document.createElement('div');
    caja.className = 'buscador';
    caja.appendChild(etiqueta);
    caja.appendChild(campo);
    caja.appendChild(recuento);
    listaBusca.parentNode.insertBefore(caja, listaBusca);

    // Sin acentos y en minúsculas: quien escribe «galeria» buscando «galería»
    // tiene que encontrarla igual.
    var llano = function (t) {
      return t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    };

    campo.addEventListener('input', function () {
      var busca = llano(campo.value.trim());
      var vistos = 0;
      entradas.forEach(function (e) {
        var vale = !busca || llano(e.texto).indexOf(busca) !== -1;
        e.li.hidden = !vale;
        if (vale) vistos++;
      });
      if (!busca) { recuento.textContent = ''; return; }
      recuento.textContent = vistos === 0
        ? 'Ninguna página coincide. Prueba con otra palabra.'
        : vistos === 1 ? '1 página coincide' : vistos + ' páginas coinciden';
    });
  }


  // ---------- Pestañas de temporada ----------
  // Preparado para futuras temporadas; hoy solo hay una. La semántica de
  // pestañas la pone el script y no el HTML, como el resto del ARIA del
  // sitio: sin JS los paneles se ven todos y unos role="tabpanel" sueltos
  // solo estorbarían.
  document.querySelectorAll('.season-tabs').forEach(function (tabs, iGrupo) {
    var buttons = Array.prototype.slice.call(tabs.querySelectorAll('button'));
    var paneles = Array.prototype.slice.call(
      tabs.parentElement.querySelectorAll('.season-panel'));
    if (!buttons.length) return;

    tabs.setAttribute('role', 'tablist');
    tabs.setAttribute('aria-label', 'Temporadas');

    var pon = function (btn) {
      var destino = btn.getAttribute('data-target');
      buttons.forEach(function (b) {
        var activo = b === btn;
        b.classList.toggle('active', activo);
        b.setAttribute('aria-selected', activo ? 'true' : 'false');
        // Solo la pestaña activa entra en el orden del tabulador: dentro de
        // un tablist se cambia de pestaña con las flechas, no con Tab.
        b.tabIndex = activo ? 0 : -1;
      });
      paneles.forEach(function (p) {
        p.hidden = p.dataset.season !== destino;
      });
    };

    buttons.forEach(function (btn, i) {
      var idBoton = 'temporada-' + iGrupo + '-' + i;
      var panel = paneles.filter(function (p) {
        return p.dataset.season === btn.getAttribute('data-target');
      })[0];

      btn.type = 'button';
      btn.id = idBoton;
      btn.setAttribute('role', 'tab');
      if (panel) {
        panel.id = panel.id || idBoton + '-panel';
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', idBoton);
        btn.setAttribute('aria-controls', panel.id);
      }

      btn.addEventListener('click', function () { pon(btn); });
      btn.addEventListener('keydown', function (e) {
        var paso = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!paso) return;
        e.preventDefault();
        var siguiente = buttons[(i + paso + buttons.length) % buttons.length];
        pon(siguiente);
        siguiente.focus();
      });
    });

    pon(buttons.filter(function (b) { return b.classList.contains('active'); })[0]
        || buttons[0]);
  });
});

