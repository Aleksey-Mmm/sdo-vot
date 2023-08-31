function SdoUtil () {}

SdoUtil.formatDurationSec = function (sec) {
  var date = new Date(null);
  date.setSeconds(sec);
  return date.toISOString().substr(11, 8);
};

SdoUtil.formatDurationSecLong = function (sec) {
  var date = new Date(null);
  date.setSeconds(sec);
  return SdoUtil.formatNumberTwoDigit(date.getUTCHours()) + " ч " + SdoUtil.formatNumberTwoDigit(date.getMinutes()) + " мин " + SdoUtil.formatNumberTwoDigit(date.getSeconds()) + " сек";
};

SdoUtil.formatNumberTwoDigit = function (num) {
  return ("0" + num).slice(-2);
};

SdoUtil.notifyValidity = function(message, elem) {
  if (elem && ("setCustomValidity" in elem) && ("reportValidity" in elem)) {
    elem.setCustomValidity(message);
    elem.reportValidity();
  } else {
    alert(message);
  }
  elem && elem.focus();
};

SdoUtil.validatePasswords = function(passwordElem, password2Elem) {
  function reset() {
    if ("setCustomValidity" in passwordElem) {
      passwordElem.setCustomValidity("");
      password2Elem.setCustomValidity("");
    }
  }
  passwordElem.onchange = password2Elem.onchange = passwordElem.onkeypress = password2Elem.onkeypress = reset;
  if (passwordElem.value === "") {
    SdoUtil.notifyValidity("Задайте пароль", passwordElem);
    return false;
  } else if (passwordElem.value !== password2Elem.value) {
    SdoUtil.notifyValidity("Пароли не совпадают", password2Elem);
    return false;
  } else {
    if(!/[0-9]/.test(passwordElem.value)) {
      SdoUtil.notifyValidity("Пароль должен содержать цифры (0-9)", passwordElem);
      return false;
    }
    if(!/[a-z]/.test(passwordElem.value)) {
      SdoUtil.notifyValidity("Пароль должен содержать буквы нижнего регистра (a-z)", passwordElem);
      return false;
    }
    if(!/[A-Z]/.test(passwordElem.value)) {
      SdoUtil.notifyValidity("Пароль должен содержать буквы верхнего регистра (A-Z)", passwordElem);
      return false;
    }
  }
  return true;
};


$(function() {
  return;
  var prevOpen;
  $("sidebar a").click(function(evt) {
    var newOpen = $(evt.target).next("submenu");
    newOpen.toggleClass("collapsed");
    if (prevOpen && newOpen[0] !== prevOpen[0]) {
      prevOpen.toggleClass("collapsed");
    }
    prevOpen = newOpen;
  });
});

$(function() {
  // function findForm(elem) {
  //   if (!elem) {
  //     return null;
  //   }
  //   if (elem.tagName === "FORM") {
  //     return elem;
  //   }
  //   return findForm(elem.parentElement);
  // }
  var blurring;
  $("*[required]").each(function(i, elem) {
    elem.onblur = function() {
      if (blurring) {
        return;
      }
      if (! ("reportValidity" in elem)) {
        console.info("No .reportValidity available, disabling skipping required checking");
        return;
      }
      blurring = true;
      setTimeout(function() {
        elem.reportValidity();
        blurring = false;
      }, 10);
    };
  })
});

//анимация каталога курсов
$(function () {
  $(".category").click(function () {
    $(this).next().toggle("slow");

    var icon = $(this).children(":first");
    if (icon.hasClass("fa-sort-down")) {
      icon.addClass("fa-caret-right");
      icon.removeClass("fa-sort-down");
    } else {
      icon.addClass("fa-sort-down");
      icon.removeClass("fa-caret-right");
    }

  });
});