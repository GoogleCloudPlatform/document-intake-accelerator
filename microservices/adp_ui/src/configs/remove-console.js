export const GlobalDebug = (function () {
    var savedConsole = console;
    /**
    * @param {boolean} debugOn
    * @param {boolean} suppressAll
    */
    return function (debugOn, suppressAll) {
      var suppress = suppressAll || false;
      if (debugOn === false) {
        // supress the default console functionality
        console = {};
        console.log = function () {};
        // supress all type of consoles
        if (suppress) {
          console.info = function () {};
          console.warn = function () {};
          console.error = function () {};
        } else {
          console.info = savedConsole.info;
          console.warn = savedConsole.warn;
          console.error = savedConsole.error;
        }
      } else {
        console = savedConsole;
      }
    };
  })();


  