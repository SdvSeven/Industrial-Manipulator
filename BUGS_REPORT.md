1. PRIORITIZED FIX PLAN (BUGS)
P0 (Critical)
[P0] UI freeze + crash при E-Stop (BUG#1)
Влияние: краш приложения + неконсистентное состояние потоков
Решение:
В MainWindow._on_emergency_stop():
if self._worker:
    self._worker.stop()
    self._worker.wait(500)  # добавить
    self._worker.deleteLater()
В CameraWorker.run():
result = hands.process(rgb)
if not self._running:
    break
Запретить deleteLater() до завершения потока
Сложность: Medium
[P0] Monkey-patching → дубли сигналов (BUG#2)
Влияние: двойные команды, некорректное управление манипулятором
Решение (вариант 1 — предпочтительный):
В CameraView:
worker_started = Signal(object)
При создании воркера:
self.worker_started.emit(worker)
В MainWindow:
cam_view.worker_started.connect(self._connect_worker_signals)
Альтернатива (временный фикс):
if not hasattr(worker, "_mw_connected"):
    connect_signals()
    worker._mw_connected = True
Сложность: Medium
P1 (High)
[P1] Двойной E-Stop при logout (BUG#3)
Влияние: дубли логов, нестабильное состояние
Решение:
Удалить:
AppState.logout():
    self.emergency_stop()  # удалить
Сложность: Low
[P1] Блокировка UI на 3 сек (BUG#4)
Влияние: плохой UX, “фриз” интерфейса
Решение:
# убрать wait()
worker.finished.connect(worker.deleteLater)
Сложность: Medium
[P1] Перегрузка UI логами (BUG#5)
Влияние: деградация производительности через 1–2 минуты
Решение:
if gesture != self._state.last_gesture:
    self._push_log_entry_to_view(...)
Сложность: Low
P2 (Medium)
[P2] GestureTracker лишняя проверка (BUG#6)
Решение: удалить if not self._history
Сложность: Low
[P2] Дублирование логов (BUG#7)
Решение:
self._all_entries = app_state.log_entries  # ссылка
Сложность: Medium
[P2] Мёртвый код (BUG#8, BUG#9)
Решение: удалить импорты + неиспользуемые параметры
Сложность: Low
2. SECURITY HARDENING PLAN
1. Auth Bypass
Риск: Critical
Исправление:
Минимум:
hash = sha256(password)
if hash != stored_hash: reject
Хранение: QSettings или локальный JSON
Дополнительно:
rate limiting (3 попытки)
UI banner: “Demo mode” если нет auth backend
2. Arbitrary File Write
Риск: Medium
Исправление:
path = QFileDialog.getSaveFileName(...)
if not path.endswith(".csv"):
    path += ".csv"
ограничение:
dialog.setDirectory(QStandardPaths.writableLocation(...))
Дополнительно:
запрет абсолютных системных путей (regex)
3. CSV Injection
Риск: Medium
Исправление:
def sanitize(val):
    if val.startswith(("=", "+", "-", "@")):
        return "'" + val
    return val
Дополнительно:
sanitize на уровне AppState (единая точка)
4. Monkey-patching (Attack Surface)
Риск: Low → Medium (в будущем)
Исправление:
Полный отказ → переход на Signals/Slots
Дополнительно:
запрет runtime mutation методов (lint rule)
5. Injection через gesture_map
Риск: High (будущий Serial exploit)
Исправление:
pattern = r"^(MOVE_[XY] [+-]\d+|GRAB|RELEASE)$"
if not re.match(pattern, cmd):
    reject
Дополнительно:
whitelist enum вместо строк
sandbox слой перед Arduino (command encoder)
3. ARCHITECTURE IMPROVEMENTS
1. Нарушение инкапсуляции (_worker доступ через 4 уровня)
Почему критично: ломает масштабируемость
Решение:
Ввести Facade API:
ControlView.get_camera()
CameraView.stop()
Эффект: слабая связанность
2. AppState перегружен
Почему критично: невозможно добавить persistence
Решение:
Разделить:
SystemState (runtime)
Config (gesture_map, speed)
EventLog
Эффект: чистая архитектура + расширяемость
3. Дублирование логов
Решение: Single Source of Truth → только AppState
Эффект: консистентность данных
4. Отсутствие persistence
Решение:
QSettings.setValue("gesture_map", json.dumps(...))
Эффект: сохранение настроек
5. Fake connection flow
Почему критично: ломает доверие UX
Решение:
Реальная проверка:
camera open()
serial port check
Эффект: корректное состояние системы
6. Жёсткий layout
Решение:
setMinimumWidth(280)
layout.setStretch(...)
Эффект: адаптивность
4. UX IMPROVEMENT PLAN
P0
Фейковое подключение
Влияние: потеря доверия
Решение:
реальный статус + fallback “device not found”
Приоритет: P0
Нет блокировки доступа в Control
Решение:
disable переход:
if state != RUNNING: block navigation
Приоритет: P0
P1
Нет feedback при CONNECTING
Решение:
spinner + disable кнопки
смена иконки
Приоритет: P1
E-Stop не меняет экран
Решение:
sidebar.set_active("Home")
Приоритет: P1
Нет визуального auth-lock
Решение:
SidebarItem[locked="true"] {
    opacity: 0.4;
}
Приоритет: P1
P2
GestureInfo без команды
Решение:
добавить:
Command: MOVE_X -10
Приоритет: P2
Нет подтверждения очистки логов
Решение:
QMessageBox.question(...)
Приоритет: P2
Фильтр команд не динамический
Решение:
combo.addItems(app_state.gesture_map.values())
Приоритет: P2
P3
ControlPanel слишком широкая
Решение: адаптивный layout
GRAB/RELEASE не выделены
Решение: цвет + размер + иконка
5. IMPLEMENTATION ROADMAP
Phase 1 (Critical)
Задачи:
Fix race condition (E-Stop)
Убрать monkey-patching
Удалить двойной logout E-Stop
Дедупликация логов
Валидация gesture_map
Блокировка Control без RUNNING
Реальный connection check
Результат:
Нет крашей
Нет двойных команд
Система безопасна для управления
Phase 2 (Stabilization)
Задачи:
Разделение AppState
Внедрение QSettings
Удаление дублирования логов
Асинхронная остановка камеры
UX фиксы (feedback, auth-lock, E-Stop redirect)
Результат:
Стабильная архитектура
Предсказуемый UX
Сохранение настроек
Phase 3 (Improvement)
Задачи:
Адаптивный UI layout
Улучшение ControlPanel
Динамические фильтры
Улучшение визуальной иерархии
Оптимизация логирования (batch/async)
Результат:
Production-ready UX
Масштабируемость
Улучшенная производительность
Итог
План выстроен по принципу:
Сначала устранение крашей и некорректного поведения (P0/P1)
Затем структурная стабилизация
В конце — UX и масштабирование
Это минимизирует риск регрессий и позволяет быстро довести систему до состояния MVP → Production-grade.