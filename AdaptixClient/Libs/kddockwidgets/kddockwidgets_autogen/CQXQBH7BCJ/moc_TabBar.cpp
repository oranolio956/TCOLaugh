/****************************************************************************
** Meta object code from reading C++ file 'TabBar.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../qtwidgets/views/TabBar.h"
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'TabBar.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 68
#error "This file was generated using the moc from 6.4.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

#ifndef Q_CONSTINIT
#define Q_CONSTINIT
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace {
struct qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar_t {
    uint offsetsAndSizes[16];
    char stringdata0[33];
    char stringdata1[19];
    char stringdata2[1];
    char stringdata3[6];
    char stringdata4[18];
    char stringdata5[13];
    char stringdata6[25];
    char stringdata7[33];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar_t qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar = {
    {
        QT_MOC_LITERAL(0, 32),  // "KDDockWidgets::QtWidgets::TabBar"
        QT_MOC_LITERAL(33, 18),  // "dockWidgetInserted"
        QT_MOC_LITERAL(52, 0),  // ""
        QT_MOC_LITERAL(53, 5),  // "index"
        QT_MOC_LITERAL(59, 17),  // "dockWidgetRemoved"
        QT_MOC_LITERAL(77, 12),  // "countChanged"
        QT_MOC_LITERAL(90, 24),  // "currentDockWidgetChanged"
        QT_MOC_LITERAL(115, 32)   // "KDDockWidgets::Core::DockWidget*"
    },
    "KDDockWidgets::QtWidgets::TabBar",
    "dockWidgetInserted",
    "",
    "index",
    "dockWidgetRemoved",
    "countChanged",
    "currentDockWidgetChanged",
    "KDDockWidgets::Core::DockWidget*"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__QtWidgets__TabBar[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       4,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       4,       // signalCount

 // signals: name, argc, parameters, tag, flags, initial metatype offsets
       1,    1,   38,    2, 0x06,    1 /* Public */,
       4,    1,   41,    2, 0x06,    3 /* Public */,
       5,    0,   44,    2, 0x06,    5 /* Public */,
       6,    1,   45,    2, 0x06,    6 /* Public */,

 // signals: parameters
    QMetaType::Void, QMetaType::Int,    3,
    QMetaType::Void, QMetaType::Int,    3,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 7,    2,

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::QtWidgets::TabBar::staticMetaObject = { {
    QMetaObject::SuperData::link<View<QTabBar>::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__QtWidgets__TabBar,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<TabBar, std::true_type>,
        // method 'dockWidgetInserted'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<int, std::false_type>,
        // method 'dockWidgetRemoved'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<int, std::false_type>,
        // method 'countChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        // method 'currentDockWidgetChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<KDDockWidgets::Core::DockWidget *, std::false_type>
    >,
    nullptr
} };

void KDDockWidgets::QtWidgets::TabBar::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<TabBar *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->dockWidgetInserted((*reinterpret_cast< std::add_pointer_t<int>>(_a[1]))); break;
        case 1: _t->dockWidgetRemoved((*reinterpret_cast< std::add_pointer_t<int>>(_a[1]))); break;
        case 2: _t->countChanged(); break;
        case 3: _t->currentDockWidgetChanged((*reinterpret_cast< std::add_pointer_t<KDDockWidgets::Core::DockWidget*>>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (TabBar::*)(int );
            if (_t _q_method = &TabBar::dockWidgetInserted; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (TabBar::*)(int );
            if (_t _q_method = &TabBar::dockWidgetRemoved; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (TabBar::*)();
            if (_t _q_method = &TabBar::countChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (TabBar::*)(KDDockWidgets::Core::DockWidget * );
            if (_t _q_method = &TabBar::currentDockWidgetChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 3;
                return;
            }
        }
    }
}

const QMetaObject *KDDockWidgets::QtWidgets::TabBar::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::QtWidgets::TabBar::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__QtWidgets__TabBar.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "Core::TabBarViewInterface"))
        return static_cast< Core::TabBarViewInterface*>(this);
    return View<QTabBar>::qt_metacast(_clname);
}

int KDDockWidgets::QtWidgets::TabBar::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = View<QTabBar>::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 4)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 4;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 4)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 4;
    }
    return _id;
}

// SIGNAL 0
void KDDockWidgets::QtWidgets::TabBar::dockWidgetInserted(int _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void KDDockWidgets::QtWidgets::TabBar::dockWidgetRemoved(int _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void KDDockWidgets::QtWidgets::TabBar::countChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 2, nullptr);
}

// SIGNAL 3
void KDDockWidgets::QtWidgets::TabBar::currentDockWidgetChanged(KDDockWidgets::Core::DockWidget * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 3, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
