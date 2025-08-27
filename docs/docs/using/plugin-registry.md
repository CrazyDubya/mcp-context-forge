# Plugin Registry

This page lists the available plugins for the MCP Gateway. These plugins can be used to extend the functionality of the gateway with new features, such as security filters, request/response transformers, and more.

<div id="plugin-registry"></div>

## Contributing a Plugin

If you have developed a plugin that you would like to share with the community, we encourage you to add it to this registry. To do so, please follow these steps:

1.  **Fork the Repository**: Fork the [mcp-context-forge](https://github.com/IBM/mcp-context-forge) repository on GitHub.
2.  **Add Your Plugin**: Add an entry for your plugin to the `docs/plugin-registry.json` file. Please ensure that your entry follows the existing schema.
3.  **Submit a Pull Request**: Create a pull request with your changes. In the pull request description, please provide a brief overview of your plugin and a link to its repository.

Our team will review your submission and, if it meets the quality standards, we will merge it into the main repository.

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
