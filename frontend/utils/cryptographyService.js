function recursiveSortAndClean(data) {
    if (typeof data === 'object' && data !== null) {
        if (Array.isArray(data)) {
            return data.map(recursiveSortAndClean);
        } else {
            const sorted = {};
            Object.keys(data).sort().forEach(key => {
                if (data[key] !== null && data[key] !== undefined) {
                    sorted[key] = recursiveSortAndClean(data[key]);
                }
            });
            return sorted;
        }
    }
    return data;
}

function generateHash(data) {
    const canonicalData = recursiveSortAndClean(data);
    const serializedData = JSON.stringify(canonicalData, (key, value) => {
        if (value === null) return undefined; // Remove nulls
        return value;
    });
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(serializedData);
    return crypto.subtle.digest('SHA-256', encodedData).then(hashBuffer => {
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    });
}

// Manual Test (Run this in your browser console)
const data1 = { name: "Fulcrum", version: 1, status: "active" };
const data2 = { version: 1, status: "active", name: "Fulcrum" };

Promise.all([generateHash(data1), generateHash(data2)]).then(([hash1, hash2]) => {
    console.log("Hash 1:", hash1);
    console.log("Hash 2:", hash2);
    console.log("Hashes match:", hash1 === hash2); // Should be true
});
