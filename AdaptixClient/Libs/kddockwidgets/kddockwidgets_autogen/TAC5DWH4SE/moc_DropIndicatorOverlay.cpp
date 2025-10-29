/****************************************************************************
** Meta object code from reading C++ file 'DropIndicatorOverlay.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../core/DropIndicatorOverlay.h"
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'DropIndicatorOverlay.h' doesn't include <QObject>."
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
struct qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay_t {
    uint offsetsAndSizes[2];
    char stringdata0[42];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay_t qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay = {
    {
        QT_MOC_LITERAL(0, 41)   // "KDDockWidgets::Core::DropIndi..."
    },
    "KDDockWidgets::Core::DropIndicatorOverlay"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__Core__DropIndicatorOverlay[] = {

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

Q_CONSTINIT const QMetaObject KDDockWidgets::Core::DropIndicatorOverlay::staticMetaObject = { {
    QMetaObject::SuperData::link<Controller::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__Core__DropIndicatorOverlay,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<DropIndicatorOverlay, std::true_type>
    >,
    nullptr
} };

void KDDockWidgets::Core::DropIndicatorOverlay::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    (void)_o;
    (void)_id;
    (void)_c;
    (void)_a;
}

const QMetaObject *KDDockWidgets::Core::DropIndicatorOverlay::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::Core::DropIndicatorOverlay::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__Core__DropIndicatorOverlay.stringdata0))
        return static_cast<void*>(this);
    return Controller::qt_metacast(_clname);
}

int KDDockWidgets::Core::DropIndicatorOverlay::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = Controller::qt_metacall(_c, _id, _a);
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
