// Système de notifications

class NotificationManager {
    constructor() {
        this.container = null;
        this.toastIdCounter = 0;
        this.eventSource = null;
        this.browserNotificationsEnabled = false;
        this.init();
    }

    init() {
        // Créer le conteneur de toasts
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);

        // Vérifier les permissions de notification navigateur
        this.checkBrowserNotificationPermission();

        // Connecter au flux SSE
        this.connectToSSE();

        console.log('✓ Système de notifications initialisé');
    }

    checkBrowserNotificationPermission() {
        if (!('Notification' in window)) {
            console.log('Les notifications navigateur ne sont pas supportées');
            return;
        }

        if (Notification.permission === 'granted') {
            this.browserNotificationsEnabled = true;
            console.log('✓ Notifications navigateur autorisées');
        } else if (Notification.permission === 'default') {
            // Afficher un banner pour demander la permission
            this.showPermissionBanner();
        }
    }

    showPermissionBanner() {
        const banner = document.createElement('div');
        banner.className = 'notification-banner';
        banner.innerHTML = `
            <span class="notification-banner-text">
                🔔 Activez les notifications pour être alerté même quand l'onglet est en arrière-plan
            </span>
            <button class="btn btn-success" id="enable-notifications">Activer</button>
            <button class="btn btn-danger" id="dismiss-notifications">Plus tard</button>
        `;

        document.body.appendChild(banner);

        document.getElementById('enable-notifications').addEventListener('click', async () => {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                this.browserNotificationsEnabled = true;
                this.showToast('success', 'Notifications activées', 'Vous recevrez maintenant des notifications système.');
            }
            banner.remove();
        });

        document.getElementById('dismiss-notifications').addEventListener('click', () => {
            banner.remove();
        });
    }

    connectToSSE() {
        try {
            this.eventSource = new EventSource('/api/stream');

            this.eventSource.onopen = () => {
                console.log('✓ Connecté au flux de notifications en temps réel');
            };

            this.eventSource.onmessage = (event) => {
                try {
                    const notification = JSON.parse(event.data);
                    this.handleNotification(notification);
                } catch (error) {
                    console.error('Erreur parsing notification:', error);
                }
            };

            this.eventSource.onerror = (error) => {
                console.error('Erreur SSE:', error);
                // Tentative de reconnexion automatique
                setTimeout(() => {
                    console.log('Tentative de reconnexion...');
                    this.connectToSSE();
                }, 5000);
            };

        } catch (error) {
            console.error('Erreur connexion SSE:', error);
        }
    }

    handleNotification(notification) {
        const { type, title, message, data } = notification;

        // Ignorer les heartbeats et les messages de connexion
        if (type === 'heartbeat' || type === 'connected') {
            return;
        }

        console.log('📢 Notification:', type, title);

        // Afficher un toast
        let toastType = 'info';
        let icon = '🔔';

        if (type === 'position_opened') {
            toastType = 'info';
            icon = '📈';
        } else if (type === 'position_closed') {
            const pnl = data?.pnl_usdt || 0;
            toastType = pnl > 0 ? 'success' : 'error';
            icon = pnl > 0 ? '🟢' : '🔴';
            if (data?.close_reason === 'LIQUIDATED') {
                icon = '💀';
            }
        }

        this.showToast(toastType, title, message, icon);

        // Notification navigateur si activée
        if (this.browserNotificationsEnabled && document.hidden) {
            this.showBrowserNotification(title, message, icon);
        }

        // Jouer un son (optionnel)
        this.playNotificationSound(type);
    }

    showToast(type, title, message, icon = null) {
        const toastId = `toast-${this.toastIdCounter++}`;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;

        // Déterminer l'icône
        if (!icon) {
            if (type === 'success') icon = '✓';
            else if (type === 'error') icon = '✗';
            else if (type === 'warning') icon = '⚠';
            else icon = 'ℹ';
        }

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
        `;

        this.container.appendChild(toast);

        // Bouton de fermeture
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toastId);
        });

        // Auto-fermeture après 7 secondes
        setTimeout(() => {
            this.removeToast(toastId);
        }, 7000);
    }

    removeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.add('closing');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    showBrowserNotification(title, message, icon) {
        try {
            const notification = new Notification(title, {
                body: message.replace(/\n/g, ' | '),
                icon: '/static/icon.png', // Vous pouvez ajouter une icône
                badge: '/static/badge.png',
                tag: 'trading-bot',
                requireInteraction: false,
                silent: false
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
            };

            // Auto-fermeture après 10 secondes
            setTimeout(() => notification.close(), 10000);

        } catch (error) {
            console.error('Erreur notification navigateur:', error);
        }
    }

    playNotificationSound(type) {
        // Son subtil pour les notifications (optionnel)
        // Vous pouvez ajouter des fichiers audio dans static/
        try {
            const audio = new Audio();
            if (type === 'position_opened') {
                // audio.src = '/static/sounds/open.mp3';
            } else if (type === 'position_closed') {
                // audio.src = '/static/sounds/close.mp3';
            }
            // audio.volume = 0.3;
            // audio.play();
        } catch (error) {
            // Ignorer les erreurs de son
        }
    }

    // Méthode pour envoyer une notification de test
    sendTestNotification() {
        this.showToast(
            'info',
            '🧪 Notification de test',
            'Si vous voyez ce message, les notifications fonctionnent correctement !'
        );
    }
}

// Instance globale
let notificationManager = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();

    // Exposer globalement pour les tests
    window.notificationManager = notificationManager;
});
