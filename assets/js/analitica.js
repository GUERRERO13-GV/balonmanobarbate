/* Club Balonmano Barbate — medición de visitas con consentimiento previo
   Desarrollo: Francisco Vidal Mateo (FranVi)

   Se mide con Vercel Web Analytics, que corre en el propio dominio: no pone
   cookies, no guarda identificadores del visitante y no manda nada a terceros.
   Por eso la CSP no necesita ninguna excepción (script-src 'self' ya cubre
   /_vercel/insights/script.js) y por eso no hace falta, en rigor, pedir
   permiso. Se pide igualmente: es lo que decidió el club, y es coherente con
   lo que ya hacen el mapa de contacto y las tablas de la federación.

   Reglas que se respetan aquí:
   - Nada se carga antes de que alguien diga que sí. Silencio = no se mide.
   - Aceptar y rechazar pesan lo mismo: mismo tamaño, mismo contraste, mismo
     sitio. Un «rechazar» escondido invalida el consentimiento.
   - La respuesta se guarda en localStorage, no en una cookie.
   - El aviso lo construye este script. Sin JavaScript no hay medición y
     tampoco un cartel que estorbe.

   Para que /_vercel/insights/script.js exista hay que tener Web Analytics
   activado en el panel de Vercel (Project → Analytics). Si no lo está, la
   petición devuelve 404 y aquí no pasa nada más: es un fallo silencioso a
   propósito, no vamos a romper la página por una métrica. */
(function () {
  'use strict';

  var CLAVE = 'analitica';
  // Ruta absoluta a propósito, y es la única del sitio: /_vercel/ lo sirve la
  // plataforma en la raíz de cada despliegue, también en las branch previews.
  var FUENTE = '/_vercel/insights/script.js';

  function leer() {
    try { return localStorage.getItem(CLAVE); } catch (e) { return null; }
  }

  function guardar(valor) {
    try { localStorage.setItem(CLAVE, valor); } catch (e) { /* modo privado */ }
  }

  function medir() {
    if (document.querySelector('script[data-analitica]')) return;
    var s = document.createElement('script');
    s.src = FUENTE;
    s.defer = true;
    s.setAttribute('data-analitica', '');
    document.head.appendChild(s);
  }

  function aviso() {
    var caja = document.createElement('div');
    caja.className = 'consentimiento';
    caja.setAttribute('role', 'dialog');
    caja.setAttribute('aria-labelledby', 'consentimiento-titulo');
    caja.setAttribute('aria-describedby', 'consentimiento-texto');

    var titulo = document.createElement('p');
    titulo.className = 'eyebrow';
    titulo.id = 'consentimiento-titulo';
    titulo.textContent = 'Medición de visitas';

    var texto = document.createElement('p');
    texto.className = 'consentimiento-texto';
    texto.id = 'consentimiento-texto';
    // Corto a propósito: en un móvil de 375 px cada frase de más es otra
    // línea tapando la página.
    texto.textContent = 'Nos gustaría contar cuántas visitas recibe la web, '
      + 'para saber qué merece la pena mantener. Se mide desde este mismo '
      + 'dominio, sin cookies y sin enviar nada a terceros. Si dices que no, '
      + 'la web funciona igual.';

    var acciones = document.createElement('div');
    acciones.className = 'consentimiento-acciones';

    function boton(etiqueta, respuesta) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn btn-ghost';
      b.textContent = etiqueta;
      b.addEventListener('click', function () {
        guardar(respuesta);
        cerrar();
        if (respuesta === 'si') medir();
      });
      return b;
    }

    var si = boton('Aceptar', 'si');
    var no = boton('Rechazar', 'no');
    acciones.appendChild(si);
    acciones.appendChild(no);

    caja.appendChild(titulo);
    caja.appendChild(texto);
    caja.appendChild(acciones);

    var devolverFoco = document.activeElement;

    function cerrar() {
      document.removeEventListener('keydown', teclas, true);
      caja.remove();
      if (devolverFoco && devolverFoco.focus) devolverFoco.focus();
    }

    function teclas(e) {
      // Escape equivale a rechazar, nunca a «ya lo decidiré luego»: cerrar
      // sin aceptar es una negativa, y dejarlo sin guardar volvería a sacar
      // el cartel en cada página.
      if (e.key === 'Escape') { guardar('no'); cerrar(); return; }
      if (e.key !== 'Tab') return;
      // Trampa de foco: mientras el aviso esté puesto, el tabulador se queda
      // dentro. Si no, se tabula por una página que aún no se puede usar.
      if (e.shiftKey && document.activeElement === si) { e.preventDefault(); no.focus(); }
      else if (!e.shiftKey && document.activeElement === no) { e.preventDefault(); si.focus(); }
    }

    document.addEventListener('keydown', teclas, true);
    document.body.appendChild(caja);
    // Un cuadro de diálogo que aparece sin foco dentro es invisible para un
    // lector de pantalla hasta que alguien tropieza con él.
    si.focus();
  }

  function arrancar() {
    var dicho = leer();
    if (dicho === 'si') { medir(); return; }
    if (dicho === 'no') return;
    aviso();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar);
  } else {
    arrancar();
  }
})();
