// Système de notifications désactivé - seules les notifications Pushover sont utilisées

// Fonction vide pour éviter les erreurs si le code est appelé ailleurs
function NotificationManager() {
    console.log('Les notifications web sont désactivées. Utilisez les notifications Pushover.');
}

NotificationManager.prototype = {
    init: function() {},
    sendTestNotification: function() {},
    showToast: function() {},
    removeToast: function() {},
    showBrowserNotification: function() {},
    playNotificationSound: function() {},
    handleNotification: function() {},
    connectToSSE: function() {},
    checkBrowserNotificationPermission: function() {},
    showPermissionBanner: function() {}
};

// Instance vide
let notificationManager = null;

// Initialisation vide
document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();
    notificationManager.init();
});
