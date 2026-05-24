<script setup lang="ts">
import { call } from 'frappe-ui'
import { Database, GitFork, Share2 } from 'lucide-vue-next'
import { computed, inject, ref } from 'vue'
import { useRoute } from 'vue-router'
import { showErrorToast } from '../helpers'
import session from '../session'
import { __ } from '../translation'
import { Workbook, workbookKey } from './workbook'
import WorkbookLineageDialog from './WorkbookLineageDialog.vue'
import WorkbookShareDialog from './WorkbookShareDialog.vue'

const workbook = inject(workbookKey) as Workbook
const route = useRoute()

const showShareDialog = ref(false)
const showLineageDialog = ref(false)
const openingSemanticModel = ref(false)

const activeQueryName = computed(() => {
	if (route.name !== 'WorkbookQuery') return ''

	const query_name = String(route.params.query_name || '')
	const index = Number(query_name)
	if (index >= 0 && workbook.doc.queries[index]) {
		return workbook.doc.queries[index].name
	}
	return query_name
})

async function openSemanticModel() {
	if (!activeQueryName.value) return

	openingSemanticModel.value = true
	try {
		const model = await call(
			'insights.insights.doctype.insights_semantic_model.insights_semantic_model.get_or_create_for_query',
			{ query: activeQueryName.value }
		) as { name: string }
		window.open(`/app/insights-semantic-model/${model.name}`, '_blank')
	} catch (error) {
		showErrorToast(error as Error, false)
	} finally {
		openingSemanticModel.value = false
	}
}
</script>

<template>
	<div v-if="workbook" class="flex gap-2">
		<Button
			v-if="workbook.canShare && !workbook.isdirty && !workbook.islocal"
			variant="outline"
			@click="showShareDialog = true"
		>
			<template #prefix>
				<Share2 class="h-4 w-4 text-gray-700" stroke-width="1.5" />
			</template>
			Share
		</Button>
		<!-- <Button
			v-show="!workbook.islocal && workbook.isdirty"
			variant="outline"
			@click="workbook.discard()"
		>
			<template #prefix>
				<Undo2 class="h-4 w-4 text-gray-700" stroke-width="1.5" />
			</template>
			Discard
		</Button>
		<Button
			v-show="workbook.islocal || workbook.isdirty"
			variant="solid"
			:loading="workbook.saving"
			@click="workbook.save()"
		>
			<template #prefix>
				<Check class="h-4 w-4 text-gray-100" stroke-width="1.5" />
			</template>
			Save
		</Button> -->
		<Dropdown
			:button="{ icon: 'more-horizontal', variant: 'outline' }"
			placement="right"
			:options="[
				{
					label: __('View Lineage'),
					icon: GitFork,
					onClick: () => (showLineageDialog = true),
				},
				session.user.has_desk_access && activeQueryName
					? {
							label: openingSemanticModel ? __('Opening Semantic Model...') : __('Semantic Model'),
							icon: Database,
							onClick: () => openSemanticModel(),
					  }
					: null,
				!workbook.doc.read_only
					? {
							label: __('Duplicate'),
							icon: 'copy',
							onClick: () => workbook.duplicate(),
					  }
					: null,
				{
					label: __('Copy JSON'),
					icon: 'copy',
					onClick: () => workbook.copy(),
				},
				!workbook.islocal
					? {
							label: __('Delete'),
							icon: 'trash-2',
							onClick: () => workbook.delete(),
					  }
					: null,
				session.user.has_desk_access
					? {
							label: __('Open in Desk'),
							icon: 'external-link',
							onClick: () => workbook.openInDesk(),
					  }
					: null,
			]"
		/>
	</div>

	<WorkbookShareDialog v-if="workbook.canShare && showShareDialog" v-model="showShareDialog" />
	<WorkbookLineageDialog v-if="showLineageDialog" v-model="showLineageDialog" />
</template>
