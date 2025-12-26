<script setup>
import { ref, onMounted, computed } from 'vue'
import { crmService } from '../services/api'

const meetings = ref([])
const deals = ref([])
const companies = ref([])
const contacts = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  title: '',
  description: '',
  date_time: '',
  duration: 60,
  location: '',
  meeting_type: 'in_person',
  status: 'scheduled',
  deal: null,
  company: null,
  participants: []
})

const defaultItem = {
  title: '',
  description: '',
  date_time: '',
  duration: 60,
  location: '',
  meeting_type: 'in_person',
  status: 'scheduled',
  deal: null,
  company: null,
  participants: []
}

const meetingTypeOptions = [
  { title: 'In Person', value: 'in_person' },
  { title: 'Virtual', value: 'virtual' },
  { title: 'Phone', value: 'phone' }
]

const statusOptions = [
  { title: 'Scheduled', value: 'scheduled' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' },
  { title: 'Cancelled', value: 'cancelled' }
]

const headers = [
  { title: 'Meeting', key: 'title', sortable: true },
  { title: 'Date & Time', key: 'date_time', sortable: true },
  { title: 'Duration', key: 'duration', sortable: true },
  { title: 'Type', key: 'meeting_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Deal', key: 'deal_title', sortable: true },
  { title: 'Company', key: 'company_name', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

const minDateTime = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
})


const sortedMeetings = computed(() => {
  const now = new Date()
  return [...meetings.value].sort((a, b) => {
    const aDate = new Date(a.date_time)
    const bDate = new Date(b.date_time)
    const aIsFuture = aDate > now
    const bIsFuture = bDate > now
    
    
    if (aIsFuture && !bIsFuture) return -1
    if (!aIsFuture && bIsFuture) return 1
    
   
    if (aIsFuture && bIsFuture) {
      return aDate - bDate
    } else {
      return bDate - aDate
    }
  })
})

const filteredMeetings = computed(() => {
  if (!search.value) return sortedMeetings.value
  const searchLower = search.value.toLowerCase()
  return sortedMeetings.value.filter(meeting =>
    meeting.title && meeting.title.toLowerCase().includes(searchLower) ||
    meeting.description && meeting.description.toLowerCase().includes(searchLower) ||
    meeting.company_name && meeting.company_name.toLowerCase().includes(searchLower) ||
    meeting.deal_title && meeting.deal_title.toLowerCase().includes(searchLower) ||
    meeting.location && meeting.location.toLowerCase().includes(searchLower)
  )
})

const activeMeetings = computed(() => {
  const now = new Date()
  return filteredMeetings.value.filter(meeting => {
    const meetingDate = new Date(meeting.date_time)
    return meetingDate > now && meeting.status !== 'cancelled'
  })
})

const pastMeetings = computed(() => {
  const now = new Date()
  return filteredMeetings.value.filter(meeting => {
    const meetingDate = new Date(meeting.date_time)
    return meetingDate <= now || meeting.status === 'cancelled'
  })
})

onMounted(async () => {
  await Promise.all([loadMeetings(), loadDeals(), loadCompanies(), loadContacts()])
})

const loadMeetings = async () => {
  loading.value = true
  try {
    meetings.value = await crmService.getMeetings()
  } catch (error) {
    console.error('Failed to load meetings:', error)
  } finally {
    loading.value = false
  }
}

const loadDeals = async () => {
  try {
    deals.value = await crmService.getDeals()
  } catch (error) {
    console.error('Failed to load deals:', error)
  }
}

const loadCompanies = async () => {
  try {
    companies.value = await crmService.getCompanies()
  } catch (error) {
    console.error('Failed to load companies:', error)
  }
}

const loadContacts = async () => {
  try {
    const allContacts = await crmService.getContacts()
    const currentUser = {
      id: 'current_user',
      first_name: 'You',
      last_name: '(System Admin)',
      email: 'admin@crm.com',
      is_current_user: true
    }
    contacts.value = [currentUser, ...allContacts]
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

const getStatusColor = (status) => {
  const colors = {
    scheduled: 'blue',
    in_progress: 'orange',
    completed: 'green',
    cancelled: 'red'
  }
  return colors[status] || 'grey'
}

const getTypeIcon = (type) => {
  const icons = {
    in_person: 'mdi-account-group',
    virtual: 'mdi-video',
    phone: 'mdi-phone'
  }
  return icons[type] || 'mdi-calendar'
}

const getUrgencyColor = (dateTime) => {
  const now = new Date()
  const meetingDate = new Date(dateTime)
  const diffHours = (meetingDate - now) / (1000 * 60 * 60)
  
  if (meetingDate <= now) return 'grey' 
  if (diffHours < 24) return 'red' 
  if (diffHours < 48) return 'orange' 
  return 'green' 
}


const formatMeetingDateTime = (dateTime) => {
  if (!dateTime) return 'No date set'
  const date = new Date(dateTime)
  
 
  const dayShort = date.toLocaleString('en-US', { weekday: 'short' })
  const dayFull = date.toLocaleString('en-US', { weekday: 'long' })
  

  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const year = date.getFullYear()
  const dateFormatted = `${month}/${day}/${year}`
  
  
  let hours12 = date.getHours()
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const ampm = hours12 >= 12 ? 'pm' : 'am'
  hours12 = hours12 % 12
  hours12 = hours12 ? hours12 : 12 
  const time12hr = `${hours12}:${minutes}${ampm}`
  

  const hours24 = date.getHours().toString().padStart(2, '0')
  const time24hr = `${hours24}${minutes}hrs`
  
  return `${dayShort}/${dayFull}, ${dateFormatted} @ ${time12hr}/${time24hr}`
}


const formatDateTime = (dateTime) => {
  if (!dateTime) return 'No date set'
  const date = new Date(dateTime)
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDuration = (minutes) => {
  if (minutes < 60) return `${minutes} min`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (remainingMinutes === 0) return `${hours} hour${hours > 1 ? 's' : ''}`
  return `${hours}h ${remainingMinutes}m`
}

const isMeetingEditable = (meeting) => {
  const now = new Date()
  const meetingDate = new Date(meeting.date_time)
  return meetingDate > now && meeting.status !== 'cancelled'
}

const editMeeting = (meeting) => {
  if (!isMeetingEditable(meeting)) {
    alert('Cannot edit past or cancelled meetings')
    return
  }
  
  editedIndex.value = meetings.value.indexOf(meeting)
  
 
  editedItem.value = {
    id: meeting.id,
    title: meeting.title,
    description: meeting.description || '',
    date_time: formatDateTimeForInput(meeting.date_time),
    duration: meeting.duration,
    location: meeting.location || '',
    meeting_type: meeting.meeting_type,
    status: meeting.status,
    deal: meeting.deal, 
    company: meeting.company, 
    participants: meeting.participants ? meeting.participants.filter(p => p !== 'current_user') : []
  }
  dialog.value = true
}

const formatDateTimeForInput = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const deleteMeeting = async (meeting) => {
  if (confirm('Are you sure you want to cancel/delete this meeting?')) {
    try {
      await crmService.updateMeeting(meeting.id, { status: 'cancelled' })
      await loadMeetings()
    } catch (error) {
      console.error('Failed to cancel meeting:', error)
    }
  }
}

const close = () => {
  dialog.value = false
  setTimeout(() => {
    editedItem.value = Object.assign({}, defaultItem)
    editedIndex.value = -1
  }, 300)
}

const save = async () => {
  try {
    const participantsToSend = editedItem.value.participants.filter(p => p !== 'current_user')
    
    const dataToSend = {
      title: editedItem.value.title,
      description: editedItem.value.description,
      date_time: editedItem.value.date_time,
      duration: editedItem.value.duration,
      location: editedItem.value.location,
      meeting_type: editedItem.value.meeting_type,
      status: editedItem.value.status,
      deal: editedItem.value.deal, 
      company: editedItem.value.company, 
      participants: participantsToSend 
    }
    
    console.log('Sending data to backend:', dataToSend)
    
    if (editedIndex.value > -1) {
      await crmService.updateMeeting(editedItem.value.id, dataToSend)
    } else {
      await crmService.createMeeting(dataToSend)
    }
    await loadMeetings()
    close()
  } catch (error) {
    console.error('Failed to save meeting:', error)
    alert('Failed to save meeting. Please check console for details.')
  }
}

const getMeetingInitials = (title) => {
  if (!title) return '?'
  const words = title.split(' ')
  if (words.length >= 2) {
    return words[0][0] + words[1][0]
  }
  return title.substring(0, 2)
}

const getMeetingColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}

const getParticipantNames = (participantIds) => {
  if (!participantIds || participantIds.length === 0) return 'No participants'
  
  return participantIds.map(id => {
    if (id === 'current_user') return 'You'
    const contact = contacts.value.find(c => c.id === id)
    return contact ? `${contact.first_name} ${contact.last_name}` : 'Unknown'
  }).join(', ')
}
</script>

<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Meetings</h1>
            <p class="text-h6 text-grey-darken-1">Schedule and track your meetings</p>
          </div>
          <v-btn color="primary" size="large" prepend-icon="mdi-calendar-plus" @click="dialog = true" elevation="2">
            Schedule Meeting
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search meetings by title, description, company, or deal..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="viewMode" mandatory variant="outlined" divided density="compact">
                <v-btn value="card" size="small"><v-icon>mdi-view-grid</v-icon></v-btn>
                <v-btn value="table" size="small"><v-icon>mdi-view-list</v-icon></v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <template v-else>
      <!-- Active/Upcoming Meetings Section -->
      <v-row v-if="activeMeetings.length > 0">
        <v-col cols="12">
          <div class="d-flex align-center mb-4">
            <v-icon color="green" class="mr-2">mdi-calendar-check</v-icon>
            <h2 class="text-h5 font-weight-bold">Upcoming Meetings ({{ activeMeetings.length }})</h2>
          </div>
        </v-col>
        
        <v-col v-for="(meeting, index) in activeMeetings" :key="meeting.id" cols="12" sm="6" md="4" lg="3">
          <v-card elevation="3" class="meeting-card h-100" hover :class="`urgency-${getUrgencyColor(meeting.date_time)}`">
            <v-card-text class="pa-4">
              <div class="d-flex align-center mb-3">
                <v-avatar :color="getMeetingColor(index)" size="48" class="mr-3">
                  <span class="text-h6 font-weight-bold text-white">
                    {{ getMeetingInitials(meeting.title) }}
                  </span>
                </v-avatar>
                <div class="flex-grow-1">
                  <h3 class="text-h6 font-weight-bold text-truncate mb-1">{{ meeting.title }}</h3>
                  <div class="d-flex align-center gap-1">
                    <v-chip :color="getStatusColor(meeting.status)" size="x-small" variant="flat" class="text-capitalize font-weight-bold">
                      {{ meeting.status }}
                    </v-chip>
                    <v-chip :color="getUrgencyColor(meeting.date_time)" size="x-small" variant="outlined" class="font-weight-bold">
                      <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                      {{ formatDateTime(meeting.date_time).split(',')[0] }}
                    </v-chip>
                  </div>
                </div>
              </div>

              <v-divider class="my-3"></v-divider>

              <div class="time-display-section mb-3 pa-3 bg-grey-lighten-4 rounded-lg">
                <div class="d-flex align-center mb-1">
                  <v-icon size="small" color="primary" class="mr-2">mdi-clock-time-four-outline</v-icon>
                  <span class="text-caption font-weight-bold text-primary">Meeting Time:</span>
                </div>
                <div class="text-body-2 font-weight-medium text-center">
                  {{ formatMeetingDateTime(meeting.date_time) }}
                </div>
                <div class="text-caption text-grey-darken-1 text-center mt-1">
                  Duration: {{ formatDuration(meeting.duration) }}
                </div>
              </div>

              <div class="meeting-details">
                <div class="d-flex align-center mb-3">
                  <v-icon size="small" class="mr-2" color="primary">{{ getTypeIcon(meeting.meeting_type) }}</v-icon>
                  <span class="text-caption font-weight-medium text-capitalize">{{ meeting.meeting_type.replace('_', ' ') }}</span>
                  <v-spacer></v-spacer>
                </div>

                <div class="d-flex align-center mb-2" v-if="meeting.company_name">
                  <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-office-building</v-icon>
                  <span class="text-caption font-weight-medium">{{ meeting.company_name }}</span>
                </div>

                <div class="d-flex align-center mb-2" v-if="meeting.deal_title">
                  <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-handshake</v-icon>
                  <span class="text-caption">{{ meeting.deal_title }}</span>
                </div>

                <div class="d-flex align-center mb-2" v-if="meeting.location">
                  <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-map-marker</v-icon>
                  <span class="text-caption text-truncate">{{ meeting.location }}</span>
                </div>

                <div class="d-flex align-center">
                  <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-account-group</v-icon>
                  <span class="text-caption text-truncate" :title="getParticipantNames(meeting.participants)">
                    {{ getParticipantNames(meeting.participants).substring(0, 30) }}
                    {{ getParticipantNames(meeting.participants).length > 30 ? '...' : '' }}
                  </span>
                </div>
              </div>
            </v-card-text>
            <v-card-actions class="pa-3 pt-0">
              <v-btn size="small" variant="text" color="primary" prepend-icon="mdi-pencil" @click="editMeeting(meeting)">
                Edit
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn size="small" variant="text" color="error" icon="mdi-close-circle" @click="deleteMeeting(meeting)" title="Cancel Meeting"></v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- Past/Cancelled Meetings Section -->
      <v-row v-if="pastMeetings.length > 0">
        <v-col cols="12">
          <div class="d-flex align-center mb-4 mt-6">
            <v-icon color="grey" class="mr-2">mdi-history</v-icon>
            <h2 class="text-h5 font-weight-bold text-grey-darken-1">Past Meetings ({{ pastMeetings.length }})</h2>
          </div>
        </v-col>
        
        <v-col v-for="(meeting, index) in pastMeetings" :key="meeting.id" cols="12" sm="6" md="4" lg="3">
          <v-card elevation="1" class="meeting-card h-100 past-meeting">
            <v-card-text class="pa-4">
              <div class="d-flex align-center mb-3">
                <v-avatar color="grey-lighten-2" size="48" class="mr-3">
                  <span class="text-h6 font-weight-bold text-grey-darken-1">
                    {{ getMeetingInitials(meeting.title) }}
                  </span>
                </v-avatar>
                <div class="flex-grow-1">
                  <h3 class="text-h6 font-weight-bold text-truncate mb-1 text-grey-darken-2">{{ meeting.title }}</h3>
                  <div class="d-flex align-center gap-1">
                    <v-chip :color="getStatusColor(meeting.status)" size="x-small" variant="flat" class="text-capitalize font-weight-bold">
                      {{ meeting.status }}
                    </v-chip>
                    <v-chip color="grey" size="x-small" variant="outlined" class="font-weight-bold">
                      <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
                      {{ formatDateTime(meeting.date_time).split(' at ')[0] }}
                    </v-chip>
                  </div>
                </div>
              </div>

              <v-divider class="my-3"></v-divider>

              
              <div class="time-display-section mb-3 pa-3 bg-grey-lighten-3 rounded-lg">
                <div class="d-flex align-center mb-1">
                  <v-icon size="small" color="grey-darken-1" class="mr-2">mdi-clock-time-four-outline</v-icon>
                  <span class="text-caption font-weight-bold text-grey-darken-1">Meeting Time:</span>
                </div>
                <div class="text-body-2 font-weight-medium text-center text-grey-darken-2">
                  {{ formatMeetingDateTime(meeting.date_time) }}
                </div>
                <div class="text-caption text-grey text-center mt-1">
                  Duration: {{ formatDuration(meeting.duration) }}
                </div>
              </div>

              <div class="meeting-details">
                <div class="text-caption text-grey-darken-2 mb-2">
                  {{ meeting.description ? meeting.description.substring(0, 80) + (meeting.description.length > 80 ? '...' : '') : 'No description' }}
                </div>
                
                <div class="d-flex align-center mb-1" v-if="meeting.deal_title">
                  <v-icon size="small" class="mr-2" color="grey">mdi-handshake</v-icon>
                  <span class="text-caption text-grey-darken-1">{{ meeting.deal_title }}</span>
                </div>
              </div>
            </v-card-text>
            <v-card-actions class="pa-3 pt-0">
              <v-btn size="small" variant="text" color="grey" prepend-icon="mdi-eye" :disabled="!isMeetingEditable(meeting)">
                View
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- No Meetings Found section -->
      <v-row v-if="filteredMeetings.length === 0">
        <v-col cols="12">
          <v-card elevation="2" class="pa-12">
            <div class="text-center">
              <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-calendar-blank</v-icon>
              <h3 class="text-h5 mb-2 text-grey-darken-1">No meetings found</h3>
              <p class="text-body-2 text-grey mb-4">
                {{ search ? 'Try adjusting your search' : 'Get started by scheduling your first meeting' }}
              </p>
              <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-calendar-plus">Schedule Meeting</v-btn>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Table View -->
    <v-row v-if="viewMode === 'table' && !loading && filteredMeetings.length > 0">
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table :headers="headers" :items="filteredMeetings" :loading="loading" items-per-page="15">
            <template v-slot:item.title="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getMeetingColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getMeetingInitials(item.title) }}
                  </span>
                </v-avatar>
                <div>
                  <span class="font-weight-medium">{{ item.title }}</span>
                  <div class="text-caption text-grey-darken-1">{{ item.description?.substring(0, 50) }}...</div>
                </div>
              </div>
            </template>
            <template v-slot:item.date_time="{ item }">
              <div class="d-flex flex-column">
                <span class="font-weight-medium">{{ formatMeetingDateTime(item.date_time) }}</span>
                <span class="text-caption text-grey-darken-1">Duration: {{ formatDuration(item.duration) }}</span>
              </div>
            </template>
            <template v-slot:item.duration="{ item }">
              <span class="font-weight-medium">{{ formatDuration(item.duration) }}</span>
            </template>
            <template v-slot:item.meeting_type="{ item }">
              <v-chip size="small" variant="tonal" :prepend-icon="getTypeIcon(item.meeting_type)" class="text-capitalize">
                {{ item.meeting_type.replace('_', ' ') }}
              </v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="small" variant="flat" class="text-capitalize font-weight-bold">
                {{ item.status }}
              </v-chip>
            </template>
            <template v-slot:item.deal_title="{ item }">
              <v-chip v-if="item.deal_title" size="small" variant="tonal" prepend-icon="mdi-handshake">
                {{ item.deal_title }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.company_name="{ item }">
              <v-chip v-if="item.company_name" size="small" variant="tonal" prepend-icon="mdi-office-building">
                {{ item.company_name }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon size="small" class="mr-2" @click="editMeeting(item)" color="primary" :disabled="!isMeetingEditable(item)">mdi-pencil</v-icon>
              <v-icon size="small" @click="deleteMeeting(item)" color="error" :disabled="!isMeetingEditable(item)">mdi-close-circle</v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Meeting Form Dialog -->
    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">{{ editedIndex === -1 ? 'mdi-calendar-plus' : 'mdi-calendar-edit' }}</v-icon>
            <span class="text-h6 font-weight-bold">{{ editedIndex === -1 ? 'Schedule New Meeting' : 'Edit Meeting' }}</span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.title"
                  label="Meeting Title *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text"
                  required
                  :rules="[v => !!v || 'Title is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.description"
                  label="Description"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text-box"
                  rows="2"
                ></v-textarea>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.date_time"
                  label="Date & Time *"
                  type="datetime-local"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-calendar-clock"
                  required
                  :rules="[v => !!v || 'Date and time is required']"
                  :min="minDateTime"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editedItem.duration"
                  label="Duration (minutes) *"
                  type="number"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-timer"
                  required
                  :rules="[v => !!v || 'Duration is required', v => v > 0 || 'Duration must be positive']"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.meeting_type"
                  :items="meetingTypeOptions"
                  label="Meeting Type *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account-group"
                  required
                  :rules="[v => !!v || 'Meeting type is required']"
                ></v-select>
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.status"
                  :items="statusOptions"
                  label="Status *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-chart-timeline-variant"
                  required
                  :rules="[v => !!v || 'Status is required']"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.location"
                  label="Location/Venue *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-map-marker"
                  required
                  :rules="[v => !!v || 'Location is required']"
                  :placeholder="editedItem.meeting_type === 'virtual' ? 'Zoom/Teams link' : 'Physical address'"
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.deal"
                  :items="deals"
                  item-title="title"
                  item-value="id"
                  label="Related Deal"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-handshake"
                  clearable
                  hint="Optional: Link this meeting to a deal"
                  persistent-hint
                ></v-select>
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.company"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Company"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-office-building"
                  clearable
                  hint="Optional: Link this meeting to a company"
                  persistent-hint
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="editedItem.participants"
                  :items="contacts.filter(c => !c.is_current_user)"
                  item-title="email"
                  item-value="id"
                  label="Participants"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account-group"
                  multiple
                  chips
                  hint="Select meeting participants (you will be automatically added)"
                  persistent-hint
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="`${item.raw.first_name} ${item.raw.last_name}`" :subtitle="item.raw.email"></v-list-item>
                  </template>
                  <template v-slot:selection="{ item }">
                    <v-chip>
                      {{ `${item.raw.first_name} ${item.raw.last_name}` }}
                    </v-chip>
                  </template>
                </v-select>
                <div class="mt-2 text-caption text-grey">
                  <v-icon size="small" color="info" class="mr-1">mdi-information</v-icon>
                  You (System Admin) will be automatically added as a participant
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="save" size="large" prepend-icon="mdi-content-save">Save Meeting</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.meeting-card {
  transition: all 0.3s ease;
  border-top: 4px solid transparent;
  border-left: 4px solid transparent;
}

.meeting-card:hover {
  transform: translateY(-2px);
}

.meeting-card.urgency-green {
  border-left-color: #4CAF50;
}

.meeting-card.urgency-orange {
  border-left-color: #FF9800;
}

.meeting-card.urgency-red {
  border-left-color: #F44336;
}

.meeting-card.past-meeting {
  opacity: 0.8;
  background-color: #fafafa;
}

.meeting-card.past-meeting:hover {
  transform: none;
  background-color: #f5f5f5;
}

.meeting-details {
  min-height: 140px;
}

.time-display-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.text-navy {
  color: #1a237e;
}

.v-chip--size-x-small {
  height: 20px;
  font-size: 10px;
}
</style>