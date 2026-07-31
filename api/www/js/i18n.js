export const translations = {
  en: {
    nav_dashboard: "Dashboard",
    nav_display: "Display",
    nav_media: "Media",
    nav_message: "Message",
    nav_system: "System",
    ota_drop: "Drop firmware binary here or click to browse",
    ota_confirm: "This will replace the running firmware and restart the device. Continue?",
  },
  fr: {
    nav_dashboard: "Tableau de bord",
    nav_display: "Affichage",
    nav_media: "Médias",
    nav_message: "Message",
    nav_system: "Système",
    ota_drop: "Glissez le binaire ici ou cliquez pour parcourir",
    ota_confirm: "Cela va remplacer le firmware en cours et redémarrer l'appareil. Continuer ?",
  },
  es: {
    nav_dashboard: "Panel",
    nav_display: "Pantalla",
    nav_media: "Medios",
    nav_message: "Mensaje",
    nav_system: "Sistema",
    ota_drop: "Arrastra el binario aquí o haz clic para buscar",
    ota_confirm: "Esto reemplazará el firmware y reiniciará el dispositivo. ¿Continuar?",
  }
};

export function setLanguage(lang) {
  const dict = translations[lang] || translations.en;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
}
