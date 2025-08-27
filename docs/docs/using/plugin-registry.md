# Plugin Registry

This page lists the available plugins for the MCP Gateway. These plugins can be used to extend the functionality of the gateway with new features, such as security filters, request/response transformers, and more.

<div id="plugin-registry"></div>

<script>
    fetch('../plugin-registry.json')
        .then(response => response.json())
        .then(data => {
            const registryDiv = document.getElementById('plugin-registry');
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200';

            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Author</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tags</th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Repository</th>
                </tr>
            `;
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            tbody.className = 'bg-white divide-y divide-gray-200';
            data.forEach(plugin => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">${plugin.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${plugin.description}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${plugin.author}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${plugin.version}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${plugin.tags.join(', ')}</td>
                    <td class="px-6 py-4 whitespace-nowrap"><a href="${plugin.repository_url}" target="_blank">Link</a></td>
                `;
                tbody.appendChild(row);
            });
            table.appendChild(tbody);

            registryDiv.appendChild(table);
        });
</script>
