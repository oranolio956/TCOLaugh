/****************************************************************************
** Meta object code from reading C++ file 'Item_p.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../core/layouting/Item_p.h"
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'Item_p.h' doesn't include <QObject>."
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
struct qt_meta_stringdata_KDDockWidgets__Core__Item_t {
    uint offsetsAndSizes[6];
    char stringdata0[26];
    char stringdata1[24];
    char stringdata2[1];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__Core__Item_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__Core__Item_t qt_meta_stringdata_KDDockWidgets__Core__Item = {
    {
        QT_MOC_LITERAL(0, 25),  // "KDDockWidgets::Core::Item"
        QT_MOC_LITERAL(26, 23),  // "onWidgetLayoutRequested"
        QT_MOC_LITERAL(50, 0)   // ""
    },
    "KDDockWidgets::Core::Item",
    "onWidgetLayoutRequested",
    ""
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__Core__Item[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       1,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags, initial metatype offsets
       1,    0,   20,    2, 0x08,    1 /* Private */,

 // slots: parameters
    QMetaType::Void,

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::Core::Item::staticMetaObject = { {
    QMetaObject::SuperData::link<Core::Object::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__Core__Item.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__Core__Item,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__Core__Item_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<Item, std::true_type>,
        // method 'onWidgetLayoutRequested'
        QtPrivate::TypeAndForceComplete<void, std::false_type>
    >,
    nullptr
} };

void KDDockWidgets::Core::Item::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Item *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->onWidgetLayoutRequested(); break;
        default: ;
        }
    }
    (void)_a;
}

const QMetaObject *KDDockWidgets::Core::Item::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::Core::Item::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__Core__Item.stringdata0))
        return static_cast<void*>(this);
    return Core::Object::qt_metacast(_clname);
}

int KDDockWidgets::Core::Item::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = Core::Object::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 1)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 1;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 1)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 1;
    }
    return _id;
}
namespace {
struct qt_meta_stringdata_KDDockWidgets__Core__ItemContainer_t {
    uint offsetsAndSizes[2];
    char stringdata0[35];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__Core__ItemContainer_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__Core__ItemContainer_t qt_meta_stringdata_KDDockWidgets__Core__ItemContainer = {
    {
        QT_MOC_LITERAL(0, 34)   // "KDDockWidgets::Core::ItemCont..."
    },
    "KDDockWidgets::Core::ItemContainer"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__Core__ItemContainer[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::Core::ItemContainer::staticMetaObject = { {
    QMetaObject::SuperData::link<Item::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__Core__ItemContainer.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__Core__ItemContainer,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__Core__ItemContainer_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<ItemContainer, std::true_type>
    >,
    nullptr
} };

void KDDockWidgets::Core::ItemContainer::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    (void)_o;
    (void)_id;
    (void)_c;
    (void)_a;
}

const QMetaObject *KDDockWidgets::Core::ItemContainer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::Core::ItemContainer::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__Core__ItemContainer.stringdata0))
        return static_cast<void*>(this);
    return Item::qt_metacast(_clname);
}

int KDDockWidgets::Core::ItemContainer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = Item::qt_metacall(_c, _id, _a);
    return _id;
}
namespace {
struct qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer_t {
    uint offsetsAndSizes[2];
    char stringdata0[38];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer_t qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer = {
    {
        QT_MOC_LITERAL(0, 37)   // "KDDockWidgets::Core::ItemBoxC..."
    },
    "KDDockWidgets::Core::ItemBoxContainer"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__Core__ItemBoxContainer[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::Core::ItemBoxContainer::staticMetaObject = { {
    QMetaObject::SuperData::link<ItemContainer::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__Core__ItemBoxContainer,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<ItemBoxContainer, std::true_type>
    >,
    nullptr
} };

void KDDockWidgets::Core::ItemBoxContainer::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    (void)_o;
    (void)_id;
    (void)_c;
    (void)_a;
}

const QMetaObject *KDDockWidgets::Core::ItemBoxContainer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::Core::ItemBoxContainer::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__Core__ItemBoxContainer.stringdata0))
        return static_cast<void*>(this);
    return ItemContainer::qt_metacast(_clname);
}

int KDDockWidgets::Core::ItemBoxContainer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = ItemContainer::qt_metacall(_c, _id, _a);
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
