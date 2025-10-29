/****************************************************************************
** Meta object code from reading C++ file 'Group.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../qtwidgets/views/Group.h"
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Group.h' doesn't include <QObject>."
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
struct qt_meta_stringdata_KDDockWidgets__QtWidgets__Group_t {
    uint offsetsAndSizes[10];
    char stringdata0[32];
    char stringdata1[22];
    char stringdata2[1];
    char stringdata3[22];
    char stringdata4[17];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__QtWidgets__Group_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__QtWidgets__Group_t qt_meta_stringdata_KDDockWidgets__QtWidgets__Group = {
    {
        QT_MOC_LITERAL(0, 31),  // "KDDockWidgets::QtWidgets::Group"
        QT_MOC_LITERAL(32, 21),  // "numDockWidgetsChanged"
        QT_MOC_LITERAL(54, 0),  // ""
        QT_MOC_LITERAL(55, 21),  // "isInMainWindowChanged"
        QT_MOC_LITERAL(77, 16)   // "isFocusedChanged"
    },
    "KDDockWidgets::QtWidgets::Group",
    "numDockWidgetsChanged",
    "",
    "isInMainWindowChanged",
    "isFocusedChanged"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__QtWidgets__Group[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       3,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: name, argc, parameters, tag, flags, initial metatype offsets
       1,    0,   32,    2, 0x06,    1 /* Public */,
       3,    0,   33,    2, 0x06,    2 /* Public */,
       4,    0,   34,    2, 0x06,    3 /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::QtWidgets::Group::staticMetaObject = { {
    QMetaObject::SuperData::link<View<QWidget>::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__QtWidgets__Group.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__QtWidgets__Group,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__QtWidgets__Group_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<Group, std::true_type>,
        // method 'numDockWidgetsChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        // method 'isInMainWindowChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        // method 'isFocusedChanged'
        QtPrivate::TypeAndForceComplete<void, std::false_type>
    >,
    nullptr
} };

void KDDockWidgets::QtWidgets::Group::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Group *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->numDockWidgetsChanged(); break;
        case 1: _t->isInMainWindowChanged(); break;
        case 2: _t->isFocusedChanged(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (Group::*)();
            if (_t _q_method = &Group::numDockWidgetsChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (Group::*)();
            if (_t _q_method = &Group::isInMainWindowChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (Group::*)();
            if (_t _q_method = &Group::isFocusedChanged; *reinterpret_cast<_t *>(_a[1]) == _q_method) {
                *result = 2;
                return;
            }
        }
    }
    (void)_a;
}

const QMetaObject *KDDockWidgets::QtWidgets::Group::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::QtWidgets::Group::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__QtWidgets__Group.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "Core::GroupViewInterface"))
        return static_cast< Core::GroupViewInterface*>(this);
    return View<QWidget>::qt_metacast(_clname);
}

int KDDockWidgets::QtWidgets::Group::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = View<QWidget>::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 3)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 3;
    }
    return _id;
}

// SIGNAL 0
void KDDockWidgets::QtWidgets::Group::numDockWidgetsChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void KDDockWidgets::QtWidgets::Group::isInMainWindowChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void KDDockWidgets::QtWidgets::Group::isFocusedChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 2, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
