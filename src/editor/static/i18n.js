(() => {
  const DEFAULT_LOCALE = "it";
  let messages = {};

  function interpolate(template, values) {
    return template.replace(/\{(\w+)\}/g, (_, key) =>
      Object.prototype.hasOwnProperty.call(values, key) ? String(values[key]) : `{${key}}`,
    );
  }

  window.t = (key, values = {}) => interpolate(messages[key] || key, values);

  window.initializeI18n = async (locale = DEFAULT_LOCALE) => {
    const response = await fetch(`/static/i18n/${locale}.json`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Unable to load locale: ${locale}`);
    }
    messages = await response.json();
    document.documentElement.lang = locale;
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      element.textContent = window.t(element.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      element.setAttribute("aria-label", window.t(element.dataset.i18nAriaLabel));
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      element.setAttribute("placeholder", window.t(element.dataset.i18nPlaceholder));
    });
  };
})();
