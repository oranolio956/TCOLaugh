/****************************************************************************
** Meta object code from reading C++ file 'DockRegistry.h'
**
** Created by: The Qt Meta Object Compiler version 68 (Qt 6.4.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../core/DockRegistry.h"
#include <QtCore/qmetatype.h>
#include <QtCore/QList>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'DockRegistry.h' doesn't include <QObject>."
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
struct qt_meta_stringdata_KDDockWidgets__DockRegistry_t {
    uint offsetsAndSizes[28];
    char stringdata0[28];
    char stringdata1[18];
    char stringdata2[33];
    char stringdata3[1];
    char stringdata4[19];
    char stringdata5[11];
    char stringdata6[19];
    char stringdata7[11];
    char stringdata8[45];
    char stringdata9[17];
    char stringdata10[33];
    char stringdata11[19];
    char stringdata12[6];
    char stringdata13[11];
};
#define QT_MOC_LITERAL(ofs, len) \
    uint(sizeof(qt_meta_stringdata_KDDockWidgets__DockRegistry_t::offsetsAndSizes) + ofs), len 
Q_CONSTINIT static const qt_meta_stringdata_KDDockWidgets__DockRegistry_t qt_meta_stringdata_KDDockWidgets__DockRegistry = {
    {
        QT_MOC_LITERAL(0, 27),  // "KDDockWidgets::DockRegistry"
        QT_MOC_LITERAL(28, 17),  // "focusedDockWidget"
        QT_MOC_LITERAL(46, 32),  // "KDDockWidgets::Core::DockWidget*"
        QT_MOC_LITERAL(79, 0),  // ""
        QT_MOC_LITERAL(80, 18),  // "containsDockWidget"
        QT_MOC_LITERAL(99, 10),  // "uniqueName"
        QT_MOC_LITERAL(110, 18),  // "containsMainWindow"
        QT_MOC_LITERAL(129, 10),  // "dockByName"
        QT_MOC_LITERAL(140, 44),  // "KDDockWidgets::DockRegistry::..."
        QT_MOC_LITERAL(185, 16),  // "mainWindowByName"
        QT_MOC_LITERAL(202, 32),  // "KDDockWidgets::Core::MainWindow*"
        QT_MOC_LITERAL(235, 18),  // "hasFloatingWindows"
        QT_MOC_LITERAL(254, 5),  // "clear"
        QT_MOC_LITERAL(260, 10)   // "affinities"
    },
    "KDDockWidgets::DockRegistry",
    "focusedDockWidget",
    "KDDockWidgets::Core::DockWidget*",
    "",
    "containsDockWidget",
    "uniqueName",
    "containsMainWindow",
    "dockByName",
    "KDDockWidgets::DockRegistry::DockByNameFlags",
    "mainWindowByName",
    "KDDockWidgets::Core::MainWindow*",
    "hasFloatingWindows",
    "clear",
    "affinities"
};
#undef QT_MOC_LITERAL
} // unnamed namespace

Q_CONSTINIT static const uint qt_meta_data_KDDockWidgets__DockRegistry[] = {

 // content:
      10,       // revision
       0,       // classname
       0,    0, // classinfo
       9,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // methods: name, argc, parameters, tag, flags, initial metatype offsets
       1,    0,   68,    3, 0x102,    1 /* Public | MethodIsConst  */,
       4,    1,   69,    3, 0x102,    2 /* Public | MethodIsConst  */,
       6,    1,   72,    3, 0x102,    4 /* Public | MethodIsConst  */,
       7,    2,   75,    3, 0x102,    6 /* Public | MethodIsConst  */,
       7,    1,   80,    3, 0x122,    9 /* Public | MethodCloned | MethodIsConst  */,
       9,    1,   83,    3, 0x102,   11 /* Public | MethodIsConst  */,
      11,    0,   86,    3, 0x102,   13 /* Public | MethodIsConst  */,
      12,    1,   87,    3, 0x02,   14 /* Public */,
      12,    0,   90,    3, 0x22,   16 /* Public | MethodCloned */,

 // methods: parameters
    0x80000000 | 2,
    QMetaType::Bool, QMetaType::QString,    5,
    QMetaType::Bool, QMetaType::QString,    5,
    0x80000000 | 2, QMetaType::QString, 0x80000000 | 8,    3,    3,
    0x80000000 | 2, QMetaType::QString,    3,
    0x80000000 | 10, QMetaType::QString,    3,
    QMetaType::Bool,
    QMetaType::Void, QMetaType::QStringList,   13,
    QMetaType::Void,

       0        // eod
};

Q_CONSTINIT const QMetaObject KDDockWidgets::DockRegistry::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_KDDockWidgets__DockRegistry.offsetsAndSizes,
    qt_meta_data_KDDockWidgets__DockRegistry,
    qt_static_metacall,
    nullptr,
    qt_incomplete_metaTypeArray<qt_meta_stringdata_KDDockWidgets__DockRegistry_t,
        // Q_OBJECT / Q_GADGET
        QtPrivate::TypeAndForceComplete<DockRegistry, std::true_type>,
        // method 'focusedDockWidget'
        QtPrivate::TypeAndForceComplete<KDDockWidgets::Core::DockWidget *, std::false_type>,
        // method 'containsDockWidget'
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QString &, std::false_type>,
        // method 'containsMainWindow'
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QString &, std::false_type>,
        // method 'dockByName'
        QtPrivate::TypeAndForceComplete<KDDockWidgets::Core::DockWidget *, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QString &, std::false_type>,
        QtPrivate::TypeAndForceComplete<KDDockWidgets::DockRegistry::DockByNameFlags, std::false_type>,
        // method 'dockByName'
        QtPrivate::TypeAndForceComplete<KDDockWidgets::Core::DockWidget *, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QString &, std::false_type>,
        // method 'mainWindowByName'
        QtPrivate::TypeAndForceComplete<KDDockWidgets::Core::MainWindow *, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QString &, std::false_type>,
        // method 'hasFloatingWindows'
        QtPrivate::TypeAndForceComplete<bool, std::false_type>,
        // method 'clear'
        QtPrivate::TypeAndForceComplete<void, std::false_type>,
        QtPrivate::TypeAndForceComplete<const QVector<QString> &, std::false_type>,
        // method 'clear'
        QtPrivate::TypeAndForceComplete<void, std::false_type>
    >,
    nullptr
} };

void KDDockWidgets::DockRegistry::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<DockRegistry *>(_o);
        (void)_t;
        switch (_id) {
        case 0: { KDDockWidgets::Core::DockWidget* _r = _t->focusedDockWidget();
            if (_a[0]) *reinterpret_cast< KDDockWidgets::Core::DockWidget**>(_a[0]) = std::move(_r); }  break;
        case 1: { bool _r = _t->containsDockWidget((*reinterpret_cast< std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast< bool*>(_a[0]) = std::move(_r); }  break;
        case 2: { bool _r = _t->containsMainWindow((*reinterpret_cast< std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast< bool*>(_a[0]) = std::move(_r); }  break;
        case 3: { KDDockWidgets::Core::DockWidget* _r = _t->dockByName((*reinterpret_cast< std::add_pointer_t<QString>>(_a[1])),(*reinterpret_cast< std::add_pointer_t<KDDockWidgets::DockRegistry::DockByNameFlags>>(_a[2])));
            if (_a[0]) *reinterpret_cast< KDDockWidgets::Core::DockWidget**>(_a[0]) = std::move(_r); }  break;
        case 4: { KDDockWidgets::Core::DockWidget* _r = _t->dockByName((*reinterpret_cast< std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast< KDDockWidgets::Core::DockWidget**>(_a[0]) = std::move(_r); }  break;
        case 5: { KDDockWidgets::Core::MainWindow* _r = _t->mainWindowByName((*reinterpret_cast< std::add_pointer_t<QString>>(_a[1])));
            if (_a[0]) *reinterpret_cast< KDDockWidgets::Core::MainWindow**>(_a[0]) = std::move(_r); }  break;
        case 6: { bool _r = _t->hasFloatingWindows();
            if (_a[0]) *reinterpret_cast< bool*>(_a[0]) = std::move(_r); }  break;
        case 7: _t->clear((*reinterpret_cast< std::add_pointer_t<QList<QString>>>(_a[1]))); break;
        case 8: _t->clear(); break;
        default: ;
        }
    }
}

const QMetaObject *KDDockWidgets::DockRegistry::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *KDDockWidgets::DockRegistry::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_KDDockWidgets__DockRegistry.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "Core::EventFilterInterface"))
        return static_cast< Core::EventFilterInterface*>(this);
    return QObject::qt_metacast(_clname);
}

int KDDockWidgets::DockRegistry::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 9)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 9;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 9)
            *reinterpret_cast<QMetaType *>(_a[0]) = QMetaType();
        _id -= 9;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
