// Telegram Web App инициализация
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Расширяем WebApp на весь экран
    tg.expand();
    
    // Устанавливаем цвет заголовка
    tg.setHeaderColor('#F9F8FF');
    
    // Готовность к показу
    tg.ready();
    
    console.log('Telegram WebApp инициализирован');
} else {
    console.log('Запуск в обычном браузере');
}

// ======================
// Обработчики навигации
// ======================

function openNav(route) {
    console.log('TODO: Открыть страницу', route);
    alert(`Страница "${route}" в разработке`);
}

function openProfile() {
    console.log('Открытие профиля');
    const profileModal = document.getElementById('profileModal');
    
    // Загружаем данные профиля
    loadProfileData();
    
    // Показываем модальное окно
    profileModal.style.display = 'flex';
    
    // Блокируем прокрутку body
    document.body.style.overflow = 'hidden';
    
    // Трекинг события
    trackUserAction('ProfileViewed', { userId: 'current_user' });
}

function closeProfile() {
    const profileModal = document.getElementById('profileModal');
    profileModal.style.display = 'none';
    
    // Разблокируем прокрутку body
    document.body.style.overflow = 'auto';
}

// Обработчики кликов по навигационным элементам
document.addEventListener('DOMContentLoaded', function() {
    // Навигационные элементы в шапке
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const route = this.getAttribute('data-route');
            openNav(route);
        });
    });
});

// ======================
// Обработчики систем
// ======================

function joinSystem(systemId) {
    console.log('TODO: Вступить в систему', systemId);
    
    // Мимикрируем процесс вступления
    const systemNames = {
        'giphy': 'Гифы',
        'mycelium': 'Мицелий', 
        'dna-codes': 'Коды ДНК',
        'ravens': 'Вороны'
    };
    
    const systemName = systemNames[systemId] || systemId;
    alert(`Заявка на вступление в систему "${systemName}" отправлена!\n\nВ реальной версии здесь будет:\n- Проверка требований\n- Отправка уведомления лидеру\n- Добавление в очередь`);
}

// ======================
// Обработчики инициатив
// ======================

function createInitiative() {
    console.log('TODO: Создать инициативу');
    alert('Создание инициативы в разработке!\n\nВ реальной версии здесь будет:\n- Форма создания инициативы\n- Выбор участников\n- Настройка целей и метрик');
}

// ======================
// Mock данные для демонстрации
// ======================

const mockData = {
    user: {
        name: "Алиса P.",
        xp: 870,
        maxXp: 1000,
        guild: "Орден броадкаста",
        profile: "INFP | P65 / A45 / E30 / I55",
        level: Math.floor(870 / 1000 * 100)
    },
    
    // Данные для полного профиля
    profileData: {
        avatar_url: "static/avatar_placeholder.svg",
        full_name: "Алиса Петрова",
        role: "R&D Lead",
        personality_16: "INTJ",
        personality_desc: "Творческий стратег, у которого на всё есть план.",
        
        // Психопрофиль карты
        psychoprofile: [
            {
                id: "cognitive_style",
                title: "Когнитивный стиль",
                insight: "Визионер-аналитик",
                description: "Быстро строит ментальные модели, опирается на факты, любит «почему?»",
                sources: "HEXACO Openness 4.5, SVS Self-Direction 6.25, Science 5.0"
            },
            {
                id: "motivation",
                title: "Мотивация",
                insight: "Достижения + смысл",
                description: "Нужен измеримый результат + общественная польза",
                sources: "SVS, MVPI"
            },
            {
                id: "social_profile",
                title: "Социальный профиль",
                insight: "Интроверт-дипломат",
                description: "Низкая потребность в смол-токе, но макс. эмпатия/гибкость",
                sources: "HPI, PANAS"
            },
            {
                id: "leadership",
                title: "Лидерство",
                insight: "Стратег-инициатор",
                description: "Высокий драйв, берёт ответственность, влияет на курс",
                sources: "HPI, PAEI"
            },
            {
                id: "resilience",
                title: "Устойчивость",
                insight: "Внешне спокойно, критику чувствует точечно",
                description: "Высокая самоэффективность. Adjustment 3.0, CD-RISC 84/100, GSE 36",
                sources: "HDS, CD-RISC, GSE"
            },
            {
                id: "risks",
                title: "Риски",
                insight: "Завышенные стандарты",
                description: "• Завышенные стандарты (Moving Toward 3.7)\n• «Тихий саботаж», если не согласен (Moving Away 3.0)\n• Возможен перфекционизм → задержка решений",
                sources: "HDS"
            },
            {
                id: "values",
                title: "Ценности",
                insight: "Инновации внутри каркаса",
                description: "Любит чёткие процессы, ясные риски — «инновации внутри каркаса»",
                sources: "Tradition 5.0, Security 5.0 (MVPI)"
            },
            {
                id: "individual_energy",
                title: "Индивидуальная энергия",
                insight: "Promotion-фокус",
                description: "Promotion-фокус 23 > Prevention 9 — тянется к возможностям, а не к избеганию угроз",
                sources: "RFQ"
            },
            {
                id: "team_role_paei",
                title: "PAEI роль в команде",
                insight: "E / P / A (умеренно) / I (слабо)",
                description: "Генерирует новое, завершает сам; нужен I-партнёр с people-фокусом",
                sources: "PAEI"
            }
        ]
    },
    
    systems: [
        {
            id: 'giphy',
            name: 'Система «Гифы»',
            icon: '📣',
            participants: 8,
            description: 'Осваивают питательную среду, превращают её в выручку.',
            leaders: 1
        },
        {
            id: 'mycelium', 
            name: 'Система «Мицелий»',
            icon: '🏛️',
            participants: 5,
            description: 'Сшивают гифы и гасят конфликты между системами.',
            leaders: 1
        },
        {
            id: 'dna-codes',
            name: 'Система «Коды ДНК»', 
            icon: '🎬',
            participants: 6,
            description: 'Отвечают на вопросы «кто мы», задают границы игры.',
            leaders: 1
        },
        {
            id: 'ravens',
            name: 'Система «Вороны»',
            icon: '🕵️‍♂️', 
            participants: 7,
            description: 'Сканируют все системы, ищут уязвимости',
            leaders: 2
        }
    ],
    
    initiatives: [
        {
            id: 1,
            title: 'Обновление системы ретроспектив',
            creator: 'Алиса P.',
            description: 'Создание более эффективного формата ретроспектив с интеграцией AI-ассистента',
            progress: 65,
            xpReward: 100,
            status: 'active'
        }
    ]
};

// ======================
// Утилиты для будущих API вызовов
// ======================

class MockAPI {
    static async getUserData() {
        // TODO: заменить на реальный API вызов
        console.log('MockAPI: Получение данных пользователя');
        return new Promise(resolve => {
            setTimeout(() => resolve(mockData.user), 500);
        });
    }
    
    static async getSystems() {
        // TODO: заменить на реальный API вызов  
        console.log('MockAPI: Получение списка систем');
        return new Promise(resolve => {
            setTimeout(() => resolve(mockData.systems), 500);
        });
    }
    
    static async getInitiatives() {
        // TODO: заменить на реальный API вызов
        console.log('MockAPI: Получение списка инициатив');
        return new Promise(resolve => {
            setTimeout(() => resolve(mockData.initiatives), 500);
        });
    }
    
    static async joinSystem(systemId) {
        // TODO: заменить на реальный API вызов
        console.log('MockAPI: Вступление в систему', systemId);
        return new Promise(resolve => {
            setTimeout(() => resolve({ success: true, message: 'Заявка отправлена' }), 1000);
        });
    }
}

// ======================
// Обработчики для мобильной версии
// ======================

function toggleMobileDrawer() {
    const drawer = document.getElementById('mobileDrawer');
    drawer.classList.toggle('open');
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('EM.Intranet Mini App загружен');
    
    // Добавляем обработчики для всех интерактивных элементов
    setupEventListeners();
    
    // Настраиваем адаптивный размер имени с задержкой
    setTimeout(adjustProfileNameFont, 100);
    
    // TODO: В будущем здесь будет загрузка реальных данных
    // loadUserData();
    // loadSystemsData(); 
    // loadInitiativesData();
});

function setupEventListeners() {
    // Клики по карточкам систем (для дополнительной интерактивности)
    const systemCards = document.querySelectorAll('.system-card');
    systemCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px)';
        });
    });
    
    // Анимация прогресс-баров
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
    
    // Обработчик выбора файла аватара
    const avatarFileInput = document.getElementById('avatarFileInput');
    if (avatarFileInput) {
        avatarFileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // Валидация файла
                if (!file.type.startsWith('image/')) {
                    alert('Выберите изображение (JPG или PNG)');
                    return;
                }
                
                if (file.size > 5 * 1024 * 1024) { // 5MB
                    alert('Размер файла не должен превышать 5MB');
                    return;
                }
                
                // Создаем превью
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('avatarPreview');
                    const placeholder = document.getElementById('uploadPlaceholder');
                    const saveBtn = document.getElementById('saveAvatarBtn');
                    
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    placeholder.style.display = 'none';
                    saveBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Закрытие модалок по клику на фон
    const profileModal = document.getElementById('profileModal');
    if (profileModal) {
        profileModal.addEventListener('click', function(e) {
            if (e.target === profileModal) {
                closeProfile();
            }
        });
    }
    
    const avatarModal = document.getElementById('avatarUploadModal');
    if (avatarModal) {
        avatarModal.addEventListener('click', function(e) {
            if (e.target === avatarModal) {
                closeAvatarUpload();
            }
        });
    }
    
    console.log('Event listeners установлены');
}

// ======================
// Функции для будущей интеграции
// ======================

// Пример функции для обновления XP
function updateUserXP(newXP) {
    // TODO: replace static XP with API
    const xpElement = document.getElementById('user-xp');
    if (xpElement) {
        xpElement.textContent = `${newXP} XP`;
    }
    console.log('XP обновлен:', newXP);
}

// Пример функции для обновления систем
function updateSystemsData(systems) {
    // TODO: populate systems list
    const systemsContainer = document.querySelector('[data-systems-placeholder]');
    console.log('Системы обновлены:', systems);
}

// Пример функции для логирования действий пользователя
function trackUserAction(action, data) {
    console.log('User Action:', action, data);
    
    // TODO: отправка аналитики
    if (window.Telegram && window.Telegram.WebApp) {
        // Можно отправлять события через Telegram WebApp API
        window.Telegram.WebApp.sendData(JSON.stringify({
            action: action,
            data: data,
            timestamp: Date.now()
        }));
    }
}

// ======================
// PROFILE FUNCTIONS
// ======================

function loadProfileData() {
    const profile = mockData.profileData;
    
    // Заполняем header данные
    document.getElementById('profileAvatar').src = profile.avatar_url;
    document.getElementById('profileFullName').textContent = profile.full_name;
    document.getElementById('profileRole').textContent = profile.role;
    
    // Заполняем personality badge
    document.getElementById('personalityType').textContent = `${profile.personality_16} — Архитектор`;
    document.getElementById('personalityDesc').textContent = profile.personality_desc;
    
    // Устанавливаем аватар в левом сайдбаре
    const sidebarAvatar = document.querySelector('.profile-avatar');
    if (sidebarAvatar && profile.avatar_url !== 'static/avatar_placeholder.svg') {
        sidebarAvatar.style.backgroundImage = `url(${profile.avatar_url})`;
        sidebarAvatar.style.backgroundSize = 'cover';
        sidebarAvatar.style.backgroundPosition = 'center';
    }
    
    // Генерируем карты психопрофиля
    generatePsychoprofileCards(profile.psychoprofile);
}

function generatePsychoprofileCards(psychoprofile) {
    const grid = document.getElementById('psychoprofileGrid');
    grid.innerHTML = '';
    
    psychoprofile.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'psycho-card';
        cardElement.innerHTML = `
            <div class="psycho-card-title">${card.title}</div>
            <div class="psycho-card-insight">${card.insight}</div>
            <div class="psycho-card-description">${card.description.replace(/\n/g, '<br>')}</div>
            <div class="psycho-card-sources">Источники: ${card.sources}</div>
        `;
        grid.appendChild(cardElement);
    });
}

// ======================
// AVATAR FUNCTIONS
// ======================

function changeAvatar() {
    const avatarModal = document.getElementById('avatarUploadModal');
    avatarModal.style.display = 'flex';
    
    // Сбрасываем состояние формы
    resetAvatarForm();
}

function closeAvatarUpload() {
    const avatarModal = document.getElementById('avatarUploadModal');
    avatarModal.style.display = 'none';
}

function resetAvatarForm() {
    const fileInput = document.getElementById('avatarFileInput');
    const preview = document.getElementById('avatarPreview');
    const placeholder = document.getElementById('uploadPlaceholder');
    const saveBtn = document.getElementById('saveAvatarBtn');
    
    fileInput.value = '';
    preview.style.display = 'none';
    placeholder.style.display = 'block';
    saveBtn.disabled = true;
}

function saveAvatar() {
    const fileInput = document.getElementById('avatarFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Выберите файл для загрузки');
        return;
    }
    
    // Симуляция загрузки
    const saveBtn = document.getElementById('saveAvatarBtn');
    saveBtn.textContent = 'Сохранение...';
    saveBtn.disabled = true;
    
    // Эмуляция API запроса
    setTimeout(() => {
        // Обновляем аватар в интерфейсе
        const previewSrc = document.getElementById('avatarPreview').src;
        document.getElementById('profileAvatar').src = previewSrc;
        
        // Обновляем аватар в шапке
        const headerAvatar = document.querySelector('.avatar-placeholder');
        if (headerAvatar) {
            headerAvatar.style.backgroundImage = `url(${previewSrc})`;
            headerAvatar.style.backgroundSize = 'cover';
            headerAvatar.style.backgroundPosition = 'center';
        }
        
        // Обновляем аватар в левом сайдбаре
        const sidebarAvatar = document.querySelector('.profile-avatar');
        if (sidebarAvatar) {
            sidebarAvatar.style.backgroundImage = `url(${previewSrc})`;
            sidebarAvatar.style.backgroundSize = 'cover';
            sidebarAvatar.style.backgroundPosition = 'center';
        }
        
        // Трекинг события
        trackUserAction('ProfilePhotoChanged', { userId: 'current_user' });
        
        // Закрываем модальное окно
        closeAvatarUpload();
        
        // Показываем уведомление
        showToast('Фото профиля успешно обновлено!', 'success');
        
        saveBtn.textContent = 'Сохранить';
        saveBtn.disabled = false;
    }, 1500);
}

function showToast(message, type = 'info') {
    // Простая имплементация toast уведомления
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#22C55E' : '#667eea'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Анимация появления
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Удаление через 3 секунды
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// ======================
// ADAPTIVE FONT SIZE
// ======================

function adjustProfileNameFont() {
    const nameElement = document.querySelector('.profile-name');
    if (!nameElement) return;
    
    // Получаем доступную ширину (ширина родителя минус отступы)
    const parentElement = nameElement.parentElement;
    const parentWidth = parentElement.offsetWidth - parseInt(getComputedStyle(parentElement).paddingLeft) - parseInt(getComputedStyle(parentElement).paddingRight);
    
    let fontSize = 18; // Начальный размер
    const minFontSize = 12; // Минимальный размер
    
    // Устанавливаем начальный размер
    nameElement.style.fontSize = fontSize + 'px';
    
    // Создаем временный элемент для измерения ширины текста
    const tempElement = document.createElement('span');
    tempElement.style.visibility = 'hidden';
    tempElement.style.position = 'absolute';
    tempElement.style.whiteSpace = 'nowrap';
    tempElement.style.fontWeight = getComputedStyle(nameElement).fontWeight;
    tempElement.style.fontFamily = getComputedStyle(nameElement).fontFamily;
    tempElement.textContent = nameElement.textContent;
    document.body.appendChild(tempElement);
    
    // Уменьшаем размер, пока текст помещается
    while (fontSize > minFontSize) {
        tempElement.style.fontSize = fontSize + 'px';
        if (tempElement.offsetWidth <= parentWidth - 10) { // Небольшой отступ
            break;
        }
        fontSize -= 1;
    }
    
    // Применяем найденный размер
    nameElement.style.fontSize = fontSize + 'px';
    
    // Удаляем временный элемент
    document.body.removeChild(tempElement);
    
    console.log(`Размер шрифта имени установлен: ${fontSize}px для ширины ${parentWidth}px`);
}

// Добавляем обработчик изменения размера окна
window.addEventListener('resize', function() {
    adjustProfileNameFont();
});

// Экспортируем функции для глобального использования
window.joinSystem = joinSystem;
window.createInitiative = createInitiative;
window.openNav = openNav;
window.openProfile = openProfile;
window.closeProfile = closeProfile;
window.changeAvatar = changeAvatar;
window.closeAvatarUpload = closeAvatarUpload;
window.saveAvatar = saveAvatar;
window.toggleMobileDrawer = toggleMobileDrawer;

console.log('EM.Intranet Mini App script готов к работе!'); 