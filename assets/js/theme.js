/* Club Balonmano Barbate — tema claro / oscuro
   Desarrollo: Fran Vidal (FranVi)

   Este archivo se carga SIN defer en el <head> a propósito: tiene que aplicar
   el tema guardado antes de que se pinte la página, o se vería un destello
   claro al entrar en modo oscuro. */
(function () {
  try {
    var guardado = localStorage.getItem('tema');
    if (guardado === 'dark' || guardado === 'light') {
      document.documentElement.setAttribute('data-theme', guardado);
    }
  } catch (e) {
    /* navegación privada o almacenamiento bloqueado: se usa la del sistema */
  }
})();
