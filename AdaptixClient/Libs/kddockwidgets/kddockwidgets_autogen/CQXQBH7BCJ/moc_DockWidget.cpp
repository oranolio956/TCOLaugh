/****************************************************************************
** Meta object code from reading C++ file 'DockWidget.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../qtwidgets/views/DockWidget.h"
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'DockWidget.h' doesn't include <QObject>."
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
struct qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget_t {
    uint offsetsAndSizes[20];
    char stringdata0[37];
    char stringdata1[15];
    char stringdata2[1];
    char stringdata3[33];
    char stringdata4[17];
    char stringdata5[17];
    char stringdata6[18];
    char stringdata7[14];
    char stringdata8[26];
    char stringdata9[20];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget_t qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget = {
    {
        QT_MOC_LITERAL(0, 36),  // "KDDockWidgets::QtWidgets::Doc..."
        QT_MOC_LITERAL(37, 14),  // "optionsChanged"
        QT_MOC_LITERAL(52, 0),  // ""
        QT_MOC_LITERAL(53, 32),  // "KDDockWidgets::DockWidgetOptions"
        QT_MOC_LITERAL(86, 16),  // "guestViewChanged"
        QT_MOC_LITERAL(103, 16),  // "isFocusedChanged"
        QT_MOC_LITERAL(120, 17),  // "isFloatingChanged"
        QT_MOC_LITERAL(138, 13),  // "isOpenChanged"
        QT_MOC_LITERAL(152, 25),  // "windowActiveAboutToChange"
        QT_MOC_LITERAL(178, 19)   // "isCurrentTabChanged"
    },
    "KDDockWidgets::QtWidgets::DockWidget",
    "optionsChanged",
    "",
    "KDDockWidgets::DockWidgetOptions",
    "guestViewChanged",
    "isFocusedChanged",
    "isFloatingChanged",
    "isOpenChanged",
    "windowActiveAboutToChange",
    "isCurrentTabChanged"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__QtWidgets__DockWidget[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       7,       // signalCount

 // signals: name, argc, parameters, tag, flags, initial metatype offsets
       1,    1,   56,    2, 0x06,    1 /* Public */,
       4,    0,   59,    2, 0x06,    3 /* Public */,
       5,    1,   60,    2, 0x06,    4 /* Public */,
       6,    1,   63,    2, 0x06,    6 /* Public */,
       7,    1,   66,    2, 0x06,    8 /* Public */,
       8,    1,   69,    2, 0x06,   10 /* Public */,
       9,    1,   72,    2, 0x06,   12 /* Public */,

 // signals: parameters
    QMetaType::Void, 0x80000000 | 3,    2,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,    2,
    QMetaType::Void, QMetaType::Bool,    2,
    QMetaType::Void, QMetaType::Bool,    2,
    QMetaType::Void, QMetaType::Bool,    2,
    QMetaType::Void, QMetaType::Bool,    2,

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::QtWidgets::DockWidget::staticMetaObject = { {
    QMetaObject::SuperData::link<QtWidgets::View<QWidget>::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__QtWidgets__DockWidget,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<DockWidget, std::true_type>,
        // method 'optionsChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<KDDockWidgets::DockWidgetOptions, std::false_type>,
        // method 'guestViewChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        // method 'isFocusedChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        // method 'isFloatingChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        // method 'isOpenChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        // method 'windowActiveAboutToChange'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        // method 'isCurrentTabChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<bool, std::false_type>
    >,
    nullptr
} };

void KDDockWidgets::QtWidgets::DockWidget::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<DockWidget *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->optionsChanged((*reinterpret_cast< std::add_pointer_t<KDDockWidgets::DockWidgetOptions>>(_a[1]))); break;
        case 1: _t->guestViewChanged(); break;
        case 2: _t->isFocusedChanged((*reinterpret_cast< std::add_pointer_t<bool>>(_a[1]))); break;
        case 3: _t->isFloatingChanged((*reinterpret_cast< std::add_pointer_t<bool>>(_a[1]))); break;
        case 4: _t->isOpenChanged((*reinterpret_cast< std::add_pointer_t<bool>>(_a[1]))); break;
        case 5: _t->windowActiveAboutToChange((*reinterpret_cast< std::add_pointer_t<bool>>(_a[1]))); break;
        case 6: _t->isCurrentTabChanged((*reinterpret_cast< std::add_pointer_t<bool>>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (DockWidget::*)(KDDockWidgets::DockWidgetOptions );
            if (_t _q_method = &DockWidget::optionsChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)();
            if (_t _q_method = &DockWidget::guestViewChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)(bool );
            if (_t _q_method = &DockWidget::isFocusedChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)(bool );
            if (_t _q_method = &DockWidget::isFloatingChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 3;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)(bool );
            if (_t _q_method = &DockWidget::isOpenChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 4;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)(bool );
            if (_t _q_method = &DockWidget::windowActiveAboutToChange; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 5;
                return;
            }
        }
        {
            using _t = void (DockWidget::*)(bool );
            if (_t _q_method = &DockWidget::isCurrentTabChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 6;
                return;
            }
        }
    }
}

const QMetaObject *KDDockWidgets::QtWidgets::DockWidget::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::QtWidgets::DockWidget::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__QtWidgets__DockWidget.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "Core::DockWidgetViewInterface"))
        return static_cast< Core::DockWidgetViewInterface*>(this);
    return QtWidgets::View<QWidget>::qt_metacast(_clname);
}

int KDDockWidgets::QtWidgets::DockWidget::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QtWidgets::View<QWidget>::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 7;
    }
    return _id;
}

// SIGNAL 0
void KDDockWidgets::QtWidgets::DockWidget::optionsChanged(KDDockWidgets::DockWidgetOptions _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void KDDockWidgets::QtWidgets::DockWidget::guestViewChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void KDDockWidgets::QtWidgets::DockWidget::isFocusedChanged(bool _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}

// SIGNAL 3
void KDDockWidgets::QtWidgets::DockWidget::isFloatingChanged(bool _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 3, _a);
}

// SIGNAL 4
void KDDockWidgets::QtWidgets::DockWidget::isOpenChanged(bool _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 4, _a);
}

// SIGNAL 5
void KDDockWidgets::QtWidgets::DockWidget::windowActiveAboutToChange(bool _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 5, _a);
}

// SIGNAL 6
void KDDockWidgets::QtWidgets::DockWidget::isCurrentTabChanged(bool _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 6, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
