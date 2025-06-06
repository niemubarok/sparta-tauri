import PouchDB, { emit } from 'pouchdb';

const db = new PouchDB('transaksi');

// Design document for transactions
const transactionViews: { _id: string, _rev?: string, views: any } = {
  _id: '_design/transaksi',
  views: {
    by_date: {
      map: function (doc: { type: string; timestamp: any; }) {
        if (doc.type === 'entry') {
          emit(doc.timestamp, 1);
        }
      }.toString(),
      reduce: '_count'
    },
    out_by_date: {
      map: function (doc: { type: string; timestamp: any; }) {
        if (doc.type === 'exit') {
          emit(doc.timestamp, 1);
        }
      }.toString(),
      reduce: '_count'
    },
    by_gate: {
      map: function (doc: { gateId: any; timestamp: any; }) {
        if (doc.gateId) {
          emit(doc.gateId + '_' + doc.timestamp, 1);
        }
      }.toString(),
      reduce: '_count'
    },
    by_plate: {
      map: function (doc: { plateNumber: any; type: any; timestamp: any; gateId: any; }) {
        if (doc.plateNumber) {
          emit(doc.plateNumber, {
            type: doc.type,
            timestamp: doc.timestamp,
            gateId: doc.gateId
          });
        }
      }.toString()
    }
  }
};

// Design document for gate operations
const gateViews: { _id: string, _rev?: string, views: any } = {
  _id: '_design/gate_operations',
  views: {
    manual_opens: {
      map: function (doc: { type: string; gateId: any; timestamp: any; userId: any; }) {
        if (doc.type === 'manual_open') {
          emit([doc.gateId, doc.timestamp], {
            userId: doc.userId
          });
        }
      }.toString(),
      reduce: '_count'
    },
    gate_status: {
      map: function (doc: { type: string; gateId: any; status: any; timestamp: any; }) {
        if (doc.type === 'gate_status') {
          emit(doc.gateId, {
            status: doc.status,
            timestamp: doc.timestamp
          });
        }
      }.toString()
    }
  }
};

async function createViews() {
  try {
    // Try to get existing design docs
    let transactionDoc: PouchDB.Core.IdMeta & PouchDB.Core.GetMeta, gateDoc: PouchDB.Core.IdMeta & PouchDB.Core.GetMeta;
    
    try {
      transactionDoc = await db.get('_design/transaksi');
      transactionViews._rev = transactionDoc._rev;
    } catch (e) {
      if (e.name !== 'not_found') throw e;
    }

    try {
      gateDoc = await db.get('_design/gate_operations');
      gateViews._rev = gateDoc._rev;
    } catch (e) {
      if (e.name !== 'not_found') throw e;
    }

    // Update or create design documents
    await Promise.all([
      db.put(transactionViews),
      db.put(gateViews)
    ]);

    console.log('✅ Views created successfully');
  } catch (error) {
    console.error('❌ Error creating views:', error);
  } finally {
    process.exit();
  }
}

createViews();
