from django.core.management.base import BaseCommand
from tweet.models import Complaint, ComplaintImage
import os

class Command(BaseCommand):
    help = 'Link old images in media/complaint_images/ to complaints by complaint_id'

    def handle(self, *args, **options):
        media_dir = 'media/complaint_images/'
        files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
        self.stdout.write(self.style.SUCCESS(f'Found {len(files)} files in {media_dir}'))

        for filename in files:
            self.stdout.write(f'\nImage file: {filename}')
            complaint_id = input('Enter complaint_id to link this image to (or leave blank to skip): ').strip()
            if not complaint_id:
                self.stdout.write(self.style.WARNING('Skipped.'))
                continue
            try:
                complaint = Complaint.objects.get(id=int(complaint_id))
                # Check if already linked
                if ComplaintImage.objects.filter(complaint=complaint, image=f'complaint_images/{filename}').exists():
                    self.stdout.write(self.style.WARNING('Already linked.'))
                    continue
                ComplaintImage.objects.create(complaint=complaint, image=f'complaint_images/{filename}')
                self.stdout.write(self.style.SUCCESS(f'Linked {filename} to complaint {complaint_id}'))
            except Complaint.DoesNotExist:
                self.stdout.write(self.style.ERROR('Complaint not found!'))

        self.stdout.write(self.style.SUCCESS('Done linking images.'))
